import json
from pathlib import Path
from typing import Any, Callable, List

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.agents.structured_output import ProviderStrategy, ToolStrategy
from langchain.messages import ToolMessage
from langchain_openai import ChatOpenAI
from tqdm import tqdm

from tracer.envs.airline import data_tools as airline_tools
from tracer.envs.airline import prompts as airline_prompts
from tracer.envs.retail import data_tools as retail_tools
from tracer.envs.retail import prompts as retail_prompts
from tracer.types import RunConfig, TracerAgentOutput


def _select_tools(env: str):
    if env == "airline":
        return airline_tools.tools
    if env == "retail":
        return retail_tools.tools
    raise ValueError(f"Unsupported domain: {env}")


def _load_system_prompt(env: str) -> str | None:
    if env == "airline":
        return airline_prompts.TASK_GENERATOR_SYSTEM_PROMPT, airline_prompts.TASK_GENERATOR_USER_PROMPT
    if env == "retail":
        return retail_prompts.TASK_GENERATOR_SYSTEM_PROMPT, retail_prompts.TASK_GENERATOR_USER_PROMPT
    raise ValueError(f"Unsupported domain: {env}")


@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""
    try:
        return handler(request)
    except Exception as e:
        # Return a custom error message to the model
        return ToolMessage(
            content=f"Tool error: Please check your input and try again, No date found for provided input. ({str(e)})",
            tool_call_id=request.tool_call["id"]
        )

class TracerAgent:

    def __init__(self, config: RunConfig):
        self.config = config
        llm = ChatOpenAI(model=config.model, temperature=config.temperature, timeout=300, verbose=config.verbose)
        tools = _select_tools(config.env)
        print("Loaded tools:", [tool.name for tool in tools])
        system_prompt, _ = _load_system_prompt(config.env)
        self.agent = create_agent(
            model=llm,
            tools=tools,
            middleware=[handle_tool_errors],
            system_prompt=system_prompt,
            response_format=ProviderStrategy(TracerAgentOutput)
        )
    

    def run(self):
        with open(self.config.trace_path, "r") as f:
            traces = json.load(f)
        if self.config.task_ids is not None:
            for task_id in tqdm(self.config.task_ids):
                result = self.step(traces[task_id])
                self.save_task(result["structured_response"], traces[task_id])
                yield task_id, result["structured_response"]
        else:
            if self.config.end_index is None:
                self.config.end_index = len(traces)
            for i in tqdm(range(self.config.start_index, self.config.end_index)):
                result = self.step(traces[i])
                self.save_task(result["structured_response"], traces[i])
                yield i, result["structured_response"]
    
    def step(self, input: dict) -> Any:
        _, user_prompt = _load_system_prompt(self.config.env)
        user_input = user_prompt.format(trace=json.dumps(input, indent=2))
        return self.agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": user_input,
                }
            ]
        })
    
    def save_task(self, result:TracerAgentOutput, trace: List) -> None:
        trace_path = Path(self.config.trace_path)
        output_path = trace_path.with_name(
            trace_path.name.replace("traces", "tasks")
        )
        if output_path.exists():
            with open(output_path, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []
        if data:
            next_task_id = max(item.get("task_id", -1) for item in data) + 1
        else:
            next_task_id = 0
        task = result.model_dump()
        task["task_id"] = next_task_id
        task["action_trace"] = trace
        data.append(task)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)