# Copyright Sierra

"""Agent that runs after the task generator to process or select generated tasks."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple, Type

from tracer2.agents.chat_react_agent import ChatReActAgent
from tracer2.envs.tool import Tool
from tracer2.prompts.task_preference import (
    PREFERENCE_SYSTEM_PROMPT,
    format_preference_user_prompt,
)
from tracer2.types import (
    Action,
    EnvInfo,
    EnvResetResponse,
    EnvResponse,
    GeneratedTaskCandidate,
    RESPOND_ACTION_FIELD_NAME,
    RESPOND_ACTION_NAME,
    Task,
)


class _PreferenceToolEnv:
    """Minimal env for ReAct-style tool use when rewriting instructions to preference form.
    Same tools and data as task generator; validates final output as JSON with preference_instructions.
    """

    def __init__(
        self,
        data_load_func,
        tools: List[Type[Tool]],
        initial_observation: str,
        expected_num_instructions: int,
    ) -> None:
        self.data_load_func = data_load_func
        self.data = data_load_func()
        self.tools_map: Dict[str, Type[Tool]] = {
            tool.get_info()["function"]["name"]: tool for tool in tools
        }
        self.tools_info = [tool.get_info() for tool in tools]
        self.task = Task(
            user_id="preference", actions=[], instruction=initial_observation, outputs=[]
        )
        self.actions: List[Action] = []
        self._initial_observation = initial_observation
        self.expected_num_instructions = expected_num_instructions
        self.final_response: Optional[str] = None

    def reset(self, task_index: Optional[int] = None) -> EnvResetResponse:
        self.data = self.data_load_func()
        self.actions = []
        self.final_response = None
        return EnvResetResponse(
            observation=self._initial_observation,
            info=EnvInfo(task=self.task, source="preference"),
        )

    def _validate_final_output(self, content: str) -> Tuple[bool, str]:
        try:
            data = json.loads(content)
        except Exception as e:
            return False, f"Invalid JSON: {e}"
        if not isinstance(data, dict) or "preference_instructions" not in data:
            return False, "JSON must contain key 'preference_instructions'"
        prefs = data["preference_instructions"]
        if not isinstance(prefs, list):
            return False, "'preference_instructions' must be a list of strings"
        if len(prefs) != self.expected_num_instructions:
            return (
                False,
                f"preference_instructions length {len(prefs)} must equal number of input instructions {self.expected_num_instructions}.",
            )
        for i, p in enumerate(prefs):
            if not isinstance(p, str):
                return False, f"preference_instructions[{i}] must be a string"
        return True, ""

    def step(self, action: Action) -> EnvResponse:
        self.actions.append(action)
        done = False
        observation = ""
        info = EnvInfo(task=self.task, source=action.name)

        if action.name == RESPOND_ACTION_NAME:
            content = action.kwargs.get(RESPOND_ACTION_FIELD_NAME, "")
            ok, err = self._validate_final_output(content)
            if ok:
                self.final_response = content
                observation = "###DONE###"
                done = True
                info.source = "respond"
            else:
                observation = (
                    "Error: output must be ONLY a JSON object with key 'preference_instructions' "
                    "(list of strings, same length as input instructions). "
                    f"Validation error: {err}"
                )
                info.source = "respond_invalid"
        elif action.name in self.tools_map:
            try:
                observation = self.tools_map[action.name].invoke(data=self.data, **action.kwargs)
            except Exception as e:
                observation = f"Error: {e}"
            info.source = action.name
        else:
            observation = f"Unknown action {action.name}"

        return EnvResponse(observation=observation, reward=0.0, done=done, info=info)


class TaskPostProcessorAgent:
    """Runs after the task generator. Processes or selects from generated task candidates.

    Default behavior: process() passes the candidate through unchanged; process_batch()
    selects the candidate with the highest reward when reward_result is available.
    Override or extend for custom logic (e.g. LLM refinement, filtering, scoring).
    """

    def __init__(
        self,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.0,
    ):
        self.model = model
        self.provider = provider
        self.temperature = temperature

    def process(
        self,
        candidate: GeneratedTaskCandidate,
        reward_result: Optional[Any] = None,
    ) -> GeneratedTaskCandidate:
        """Process a single candidate (e.g. refine, validate). Default: pass-through."""
        return candidate

    def add_preference_instructions(
        self,
        candidate: GeneratedTaskCandidate,
        data_load_func,
        tools: List[Type[Tool]],
        max_steps: int = 50,
    ) -> Tuple[Optional[List[str]], List[Dict[str, Any]]]:
        """Rewrite the candidate's instructions into preference form using the same tools as the generator.

        Uses tools to look up details (e.g. flight time, cabin) and produces preference-style
        instructions (e.g. "I want to fly in the evening") when there are options. Does not
        modify the candidate.

        Returns:
            (preference_instructions list or None, trajectory messages from the ReAct run).
        """
        empty: Tuple[Optional[List[str]], List[Dict[str, Any]]] = (None, [])
        if not candidate.instructions:
            return empty
        if self.model is None or self.provider is None:
            return empty

        initial_observation = format_preference_user_prompt(
            candidate.story or "", candidate.instructions
        )

        env = _PreferenceToolEnv(
            data_load_func=data_load_func,
            tools=tools,
            initial_observation=initial_observation,
            expected_num_instructions=len(candidate.instructions),
        )

        wiki = (
            PREFERENCE_SYSTEM_PROMPT
            + "\n\nWhen you are ready to finish, use Action with name='respond' and arguments {\"content\": <JSON>}."
        )

        react_agent = ChatReActAgent(
            tools_info=[t.get_info() for t in tools],
            wiki=wiki,
            model=self.model,
            provider=self.provider,
            use_reasoning=True,
            temperature=self.temperature,
        )

        try:
            res = react_agent.solve(env=env, task_index=0, max_num_steps=max_steps)
            trajectory = res.messages
        except Exception:
            return empty

        if env.final_response is None:
            return (None, trajectory)

        try:
            data = json.loads(env.final_response)
            prefs = data.get("preference_instructions")
            if isinstance(prefs, list) and len(prefs) == len(candidate.instructions):
                return ([str(p) for p in prefs], trajectory)
        except Exception:
            pass
        return (None, trajectory)
