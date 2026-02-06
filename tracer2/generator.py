import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Allow running as a script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

load_dotenv()

import litellm

litellm.drop_params = True

from tracer2.agents.task_generator_agent import TraceTaskGeneratorAgent
from tracer2.agents.task_post_processor_agent import TaskPostProcessorAgent
from tracer2.envs.base import Env
from tracer2.envs.user import UserStrategy
from tracer2.types import Task


def _default_output_path(trace_path: str) -> str:
    p = Path(trace_path)
    name = p.name
    if "traces" in name:
        name = name.replace("traces", "generated_tasks")
    else:
        name = name + ".generated_tasks.json"
    return str(p.with_name(name))


def _build_airline_env(
    task: Task, user_strategy: str, user_model: str, user_provider: str, tools_mode: str
) -> Env:
    from tracer2.envs.airline import tools as airline_tools
    from tracer2.envs.airline.data import load_data
    from tracer2.envs.airline.reverse_tools import ALL_TOOLS as REVERSE_TOOLS
    from tracer2.envs.airline.rules import RULES
    from tracer2.envs.airline.wiki import WIKI

    env = Env(
        data_load_func=load_data,
        tools=airline_tools.ALL_TOOLS if tools_mode == "forward" else REVERSE_TOOLS,
        tasks=[task],
        wiki=WIKI,
        rules=RULES,
        user_strategy=user_strategy,
        user_model=user_model,
        user_provider=user_provider,
        task_index=0,
        enable_reward=True,
    )
    env.terminate_tools = ["transfer_to_human_agents"]
    return env


def _build_retail_env(
    task: Task, user_strategy: str, user_model: str, user_provider: str, tools_mode: str
) -> Env:
    from tracer2.envs.retail import tools as retail_tools
    from tracer2.envs.retail.data import load_data
    from tracer2.envs.retail.reverse_tools import ALL_TOOLS as REVERSE_TOOLS
    from tracer2.envs.retail.rules import RULES
    from tracer2.envs.retail.wiki import WIKI

    env = Env(
        data_load_func=load_data,
        tools=retail_tools.ALL_TOOLS if tools_mode == "forward" else REVERSE_TOOLS,
        tasks=[task],
        wiki=WIKI,
        rules=RULES,
        user_strategy=user_strategy,
        user_model=user_model,
        user_provider=user_provider,
        task_index=0,
        enable_reward=True,
    )
    env.terminate_tools = ["transfer_to_human_agents"]
    return env


def _combine_instruction(user_id: str, instructions: List[str]) -> str:
    """Create a single 2nd-person instruction with the goals (same as generate_verify)."""
    if len(instructions) == 1:
        goals = f"You want: {instructions[0]}"
    else:
        goal_lines = [f"{i+1}. {inst}" for i, inst in enumerate(instructions)]
        goals = "You want to accomplish these, in order:\n" + "\n".join(goal_lines)
    return f"You are {user_id}. {goals}"


def parse_args():
    p = argparse.ArgumentParser(
        description="Generate tasks from traces, build env, and compute reward via env.calculate_reward()."
    )
    p.add_argument(
        "--env",
        default="airline",
        choices=["airline", "retail"],
        help="Domain env.",
    )
    p.add_argument(
        "--trace-path",
        default="output/traces/airline_adjacency_matrix_0.0_traces.json",
        help="Path to traces JSON file.",
    )
    p.add_argument("--output-path", default=None, help="Where to write generated tasks JSON.")

    p.add_argument("--generator-model-provider", default="openai")
    p.add_argument("--generator-model", default="gpt-5.2")
    p.add_argument("--generator-temperature", type=float, default=0.2)

    p.add_argument("--user-model-provider", default="openai")
    p.add_argument("--user-model", default="gpt-4o")
    p.add_argument(
        "--user-strategy",
        default="llm",
        choices=[u.value for u in UserStrategy],
    )

    p.add_argument("--start-index", "--start-idx", type=int, default=0)
    p.add_argument("--end-index", "--end-idx", type=int, default=None)
    p.add_argument("--task-ids", nargs="*", default=None)
    p.add_argument(
        "--tasks-per-trace",
        type=int,
        default=3,
        help="Number of tasks to generate per trace (default: 3).",
    )

    return p.parse_args()


def main():
    args = parse_args()
    with open(args.trace_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    # Support both `*_traces.json` (list of traces) and `*_tasks.json` (list of dicts with action_trace).
    if (
        isinstance(loaded, list)
        and len(loaded) > 0
        and isinstance(loaded[0], dict)
        and "action_trace" in loaded[0]
    ):
        traces = [item.get("action_trace") for item in loaded]
    else:
        traces = loaded

    output_path = args.output_path or _default_output_path(args.trace_path)
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    # Select env-specific data loader, tools, prompts, and env builder (same as generate_verify)
    if args.env == "airline":
        from tracer2.envs.airline.data import load_data
        from tracer2.envs.airline.reverse_tools import ALL_TOOLS as REVERSE_TOOLS
        from tracer2.prompts.task_generator_airline import SYSTEM_PROMPT, USER_PROMPT

        build_env = _build_airline_env
    elif args.env == "retail":
        from tracer2.envs.retail.data import load_data
        from tracer2.envs.retail.reverse_tools import ALL_TOOLS as REVERSE_TOOLS
        from tracer2.prompts.task_generator_retail import SYSTEM_PROMPT, USER_PROMPT

        build_env = _build_retail_env
    else:
        raise ValueError(f"Unsupported env: {args.env}")

    generator = TraceTaskGeneratorAgent(
        tools=REVERSE_TOOLS,
        data_load_func=load_data,
        model=args.generator_model,
        provider=args.generator_model_provider,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=USER_PROMPT,
        temperature=args.generator_temperature,
    )

    post_processor = TaskPostProcessorAgent(
        model=args.generator_model,
        provider=args.generator_model_provider,
        temperature=0.0,
    )

    if args.task_ids is not None and len(args.task_ids) > 0:
        idxs = [int(x) for x in args.task_ids]
    else:
        end = args.end_index if args.end_index is not None else len(traces)
        idxs = list(range(args.start_index, min(end, len(traces))))

    results: List[Dict[str, Any]] = []
    for idx in idxs:
        trace = traces[idx]

        print(f"\n{'='*60}")
        print(f"Trace idx={idx} (generating {args.tasks_per_trace} tasks)")
        print(f"{'='*60}")

        batch_candidates: List[tuple] = []  # (candidate, reward_result, run, result_dict or None)
        for run in range(args.tasks_per_trace):
            try:
                # Step 1: Generate task candidate (same as generate_verify)
                (
                    candidate,
                    generator_messages,
                    _,
                    _,
                ) = generator.generate(trace=trace, attempt=0, verifier_feedback=None)

                print(f"  [run {run}] User ID: {candidate.user_id}")
                print(f"  [run {run}] Story: {candidate.story[:80]}...")
                print(f"  [run {run}] Num instructions: {len(candidate.instructions)}")

                combined_instruction = _combine_instruction(
                    user_id=candidate.user_id,
                    instructions=candidate.instructions,
                )

                # Step 2: Build Task and env (same as generate_verify)
                task = Task(
                    user_id=candidate.user_id,
                    instruction=candidate.instructions,
                    actions=candidate.actions or [],
                    outputs=[],
                )
                env = build_env(
                    task=task,
                    user_strategy=args.user_strategy,
                    user_model=args.user_model,
                    user_provider=args.user_model_provider,
                    tools_mode="forward",
                )

                # Step 3: Get reward via env.calculate_reward() (replays task.actions internally)
                env.reset(task_index=0)
                # reward_result = env.calculate_reward()
                # reward_result_dump = reward_result.model_dump()

                result_dict = {
                    "task_id": idx,
                    "run": run,
                    "user_id": candidate.user_id,
                    "instructions": candidate.instructions,
                    "instruction": combined_instruction,
                    "story": candidate.story,
                    "action_trace": candidate.action_trace,
                    "ground_truth_actions": [a.model_dump() for a in (candidate.actions or [])],
                    # "reward_result": reward_result_dump,
                    "generator_traj": generator_messages,
                }
                # Step 4: Preference agent rewrites instructions to preference form (same tools as generator); add new keys only
                try:
                    preference_instructions, preference_traj = post_processor.add_preference_instructions(
                        candidate, load_data, REVERSE_TOOLS
                    )
                    if preference_instructions is not None:
                        result_dict["preference_instructions"] = preference_instructions
                        print(f"  [preference] added {len(preference_instructions)} preference instructions")
                    result_dict["preference_traj"] = preference_traj
                except Exception as pref_err:
                    print(f"  [preference] skip: {pref_err}")
                    result_dict["preference_traj"] = []
                batch_candidates.append((candidate, run, result_dict))
                print(f"  ✓ Success idx={idx} run={run}")

            except Exception as e:
                print(f"  ✗ Failed idx={idx} run={run}: {e}")
                results.append(
                    {
                        "task_id": idx,
                        "run": run,
                        "error": str(e),
                        "failed": True,
                    }
                )

        for _, _, result_dict in batch_candidates:
            results.append(result_dict)

        # Checkpoint after each trace (all runs)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

    successful = len([r for r in results if not r.get("failed", False)])
    print(f"\nCompleted: {successful}/{len(results)} tasks successfully generated")
    print(f"Saved to {out_p}")


if __name__ == "__main__":
    main()
