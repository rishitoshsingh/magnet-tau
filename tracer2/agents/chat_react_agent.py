# Copyright Sierra

import json
from typing import Any, Dict, List, Optional, Tuple

from litellm import completion

from tracer2.agents.base import Agent
from tracer2.envs.base import Env
from tracer2.types import (
    RESPOND_ACTION_FIELD_NAME,
    RESPOND_ACTION_NAME,
    Action,
    SolveResult,
)


class ChatReActAgent(Agent):
    def __init__(
        self,
        tools_info: List[Dict[str, Any]],
        wiki: str,
        model: str,
        provider: str,
        use_reasoning: bool = True,
        temperature: float = 0.0,
        api_base: Optional[str] = None,
    ) -> None:
        print(f"Initializing ChatReActAgent with model={model}, provider={provider}, use_reasoning={use_reasoning}, temperature={temperature}, api_base={api_base}")
        instruction = REACT_INSTRUCTION if use_reasoning else ACT_INSTRUCTION
        self.prompt = (
            wiki + "\n#Available tools\n" + json.dumps(tools_info) + instruction
        )
        self.model = model
        self.provider = provider
        self.temperature = temperature
        self.use_reasoning = use_reasoning
        self.tools_info = tools_info
        self.api_base = api_base
    def _extract_first_action(self, content: str) -> Optional[Tuple[Dict[str, Any], int]]:
        """Best-effort extraction of the first valid Action JSON object from a ReAct-style message.

        Returns (action_dict, end_index) where end_index is the end position (exclusive)
        of the extracted JSON object in the original content. This lets us normalize the
        logged assistant message to the *single* step that will actually be executed.

        Handles cases where the model emits multiple Action blocks or adds extra text.
        """
        if "Action:" not in content:
            return None

        search_from = 0
        while True:
            action_idx = content.find("Action:", search_from)
            if action_idx == -1:
                return None

            start = content.find("{", action_idx)
            if start == -1:
                search_from = action_idx + len("Action:")
                continue

            depth = 0
            end: Optional[int] = None
            for j in range(start, len(content)):
                ch = content[j]
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        end = j + 1
                        break

            if end is None:
                search_from = action_idx + len("Action:")
                continue

            candidate = content[start:end].strip()
            try:
                parsed = json.loads(candidate)
            except Exception:
                search_from = action_idx + len("Action:")
                continue

            if isinstance(parsed, dict):
                return parsed, end

            search_from = action_idx + len("Action:")
        # Scan each Action: block and attempt to parse the first balanced JSON object.
        parts = content.split("Action:")[1:]
        for part in parts:
            start = part.find("{")
            if start == -1:
                continue
            depth = 0
            end = None
            for j, ch in enumerate(part[start:], start=start):
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        end = j + 1
                        break
            if end is None:
                continue
            candidate = part[start:end].strip()
            try:
                parsed = json.loads(candidate)
            except Exception:
                continue
            if isinstance(parsed, dict):
                return parsed
        return None

    def generate_next_step(
        self, messages: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], Action, float]:
        completion_kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }

        completion_kwargs["custom_llm_provider"] = self.provider
        if self.api_base is not None:
            completion_kwargs["api_base"] = self.api_base

        res = completion(**completion_kwargs)
        message = res.choices[0].message
        content = message.content or ""

        cost = (getattr(res, "_hidden_params", None) or {}).get("response_cost") or 0.0

        action_info = self._extract_first_action(content)
        if not action_info:
            action = Action(
                name=RESPOND_ACTION_NAME,
                kwargs={RESPOND_ACTION_FIELD_NAME: content.strip()},
            )
            return message.model_dump(), action, cost

        action_parsed, action_end = action_info
        # Normalize the logged content to the first executed Thought/Action block.
        message_dict = message.model_dump()
        message_dict["content"] = content[:action_end].strip()

        name = action_parsed.get("name")
        arguments = action_parsed.get("arguments")
        if not isinstance(name, str):
            action = Action(
                name=RESPOND_ACTION_NAME,
                kwargs={RESPOND_ACTION_FIELD_NAME: content.strip()},
            )
            return message_dict, action, cost
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except Exception:
                arguments = {}
        if not isinstance(arguments, dict):
            action = Action(
                name=RESPOND_ACTION_NAME,
                kwargs={RESPOND_ACTION_FIELD_NAME: content.strip()},
            )
            return message_dict, action, cost

        # Ensure respond content is always a string (APIs may return parsed dict)
        if name == RESPOND_ACTION_NAME and RESPOND_ACTION_FIELD_NAME in arguments:
            raw = arguments[RESPOND_ACTION_FIELD_NAME]
            if isinstance(raw, dict):
                arguments = {**arguments, RESPOND_ACTION_FIELD_NAME: json.dumps(raw)}

        action = Action(name=name, kwargs=arguments)
        return message_dict, action, cost

    def _extract_thought(self, content: str) -> Optional[str]:
        """Extract the Thought line(s) from ReAct-style content (between Thought: and Action:)."""
        if "Thought:" not in content or "Action:" not in content:
            return None
        start = content.find("Thought:") + len("Thought:")
        end = content.find("Action:", start)
        if end == -1:
            return None
        return content[start:end].strip() or None

    def solve(
        self, env: Env, task_index: Optional[int] = None, max_num_steps: int = 30, print_thoughts: bool = False
    ) -> SolveResult:
        response = env.reset(task_index=task_index)
        reward = 0.0
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": response.observation},
        ]
        total_cost = 0.0
        info = {}
        for step in range(max_num_steps):
            message, action, cost = self.generate_next_step(messages)
            if print_thoughts:
                content = (message.get("content") or "").strip()
                thought = self._extract_thought(content)
                if thought:
                    print(f"[Step {step + 1}] Thought: {thought}")
                if action.name == "think":
                    think_text = action.kwargs.get("thought", "")
                    if think_text:
                        print(f"[Step {step + 1}] Think tool: {think_text}")
            # else:
            #     print(f"[Step {step + 1}] Action: {action.name}, Arguments: {action.kwargs}")
            response = env.step(action)
            obs = response.observation
            reward = response.reward
            info = {**info, **response.info.model_dump()}
            if action.name != RESPOND_ACTION_NAME:
                obs = "API output: " + obs
            messages.extend(
                [
                    message,
                    {"role": "user", "content": obs},
                ]
            )
            total_cost += cost
            if response.done:
                break
        return SolveResult(
            messages=messages,
            reward=reward,
            info=info,
        )


REACT_INSTRUCTION = f"""
# Instruction
You need to act as an agent that use the above tools to help the user according to the above policy.

At each step, your generation should have exactly the following format:
Thought:
<A single line of reasoning to process the context and inform the decision making. Do not include extra lines.>
Action:
{{"name": <The name of the action>, "arguments": <The arguments to the action in json format>}}

The Action will be parsed, so it must be valid JSON.

You should not use made-up or placeholder arguments.

For example, if the user says "I want to know the current weather of San Francisco", and there is such a tool available
{{
    "type": "function",
    "function": {{
        "name": "get_current_weather",
        "description": "Get the current weather",
        "parameters": {{
            "type": "object",
            "properties": {{
                "location": {{
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                }},
                "format": {{
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The temperature unit to use. Infer this from the users location.",
                }},
            }},
            "required": ["location", "format"],
        }},
    }}
}}

Your response can be like this:
Thought:
Since the user asks for the weather of San Francisco in USA, the unit should be in fahrenheit. I can query get_current_weather to get the weather.
Action:
{{"name": "get_current_weather", "arguments": {{"location": "San Francisco, CA", "format": "fahrenheit"}}}}

And if the tool returns "70F", your response can be:
Thought:
I can answer the user now.
Action:
{{"name": {RESPOND_ACTION_NAME}, "arguments": {{"{RESPOND_ACTION_FIELD_NAME}": "The current weather of San Francisco is 70F."}}}}

Try to be helpful and always follow the policy.
"""


ACT_INSTRUCTION = f"""
# Instruction
You need to act as an agent that use the above tools to help the user according to the above policy.

At each step, your generation should have exactly the following format:

Action:
{{"name": <The name of the action>, "arguments": <The arguments to the action in json format>}}

You should not use made-up or placeholder arguments.

The Action will be parsed, so it must be valid JSON.

For example, if the user says "I want to know the current weather of San Francisco", and there is such a tool available
```json
{{
    "type": "function",
    "function": {{
        "name": "get_current_weather",
        "description": "Get the current weather",
        "parameters": {{
            "type": "object",
            "properties": {{
                "location": {{
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                }},
                "format": {{
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The temperature unit to use. Infer this from the users location.",
                }},
            }},
            "required": ["location", "format"],
        }},
    }}
}}
```

Your response can be like this:
Action:
{{"name": "get_current_weather", "arguments": {{"location": "San Francisco, CA", "format": "fahrenheit"}}}}

And if the tool returns "70F", your response can be:
Action:
{{"name": {RESPOND_ACTION_NAME}, "arguments": {{"{RESPOND_ACTION_FIELD_NAME}": "The current weather of San Francisco is 70F."}}}}

Try to be helpful and always follow the policy. Always make sure you generate valid JSON only.
"""
