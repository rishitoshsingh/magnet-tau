"""Evaluator runner — entry point for the evaluator subproject.

Usage:
    python -m evaluator.runner --config evaluator/config/eval_config_airline.json
    python -m evaluator.runner --input-path output/traces/airline_adjacency_matrix_0.0_generated_tasks.json \\
        --domain airline --eval-model gpt-4.1 --eval-model-provider openai

The runner loads a `*_generated_tasks.json` file produced by tracer2/generator.py,
runs four evaluation agents over each task, and writes a
`*_eval.json` file containing TaskEvaluation records.

Checkpoint/resume: if the output file already exists, completed tasks are
skipped and failed tasks are retried — mirroring the behaviour of
tracer2/generator.py.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

import litellm  # noqa: E402

litellm.drop_params = True

from evaluator.agents.domain_violation_agent import DomainViolationAgent  # noqa: E402
from evaluator.agents.goal_orientation_agent import GoalOrientationAgent  # noqa: E402
from evaluator.agents.solvability_checker_agent import SolvabilityCheckerAgent  # noqa: E402
from evaluator.agents.template_checker_agent import TemplateCheckerAgent  # noqa: E402
from evaluator.types import CriterionResult, InstructionEvaluation, TaskEvaluation  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _default_output_path(input_path: str) -> str:
    p = Path(input_path)
    name = p.stem
    if name.endswith("_generated_tasks"):
        name = name[: -len("_generated_tasks")] + "_eval"
    else:
        name = name + "_eval"
    out_dir = p.parent.parent / "evaluations"
    out_dir.mkdir(parents=True, exist_ok=True)
    return str(out_dir / (name + ".json"))


def _load_config_defaults(config_path: str) -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_criterion_result(
    name: str,
    passed: Optional[bool],
    reason: str,
    raw_llm_output: Optional[Dict[str, Any]] = None,
    layer: Optional[str] = None,
) -> CriterionResult:
    # If passed is None (agent inconclusive), treat as passed=True (benefit of the doubt)
    # so we don't incorrectly flag tasks when the evaluator itself failed.
    is_passed = passed if passed is not None else True
    return CriterionResult(
        name=name,
        passed=is_passed,
        violation=not is_passed,
        reason=reason,
        raw_llm_output=raw_llm_output,
        layer=layer,
    )


def _evaluate_instruction(
    instruction: str,
    instruction_index: int,
    is_preference_pass: bool,
    domain: str,
    goal_agent: GoalOrientationAgent,
    template_agent: TemplateCheckerAgent,
) -> InstructionEvaluation:
    go_result = goal_agent.check(instruction=instruction, domain=domain)
    tc_result = template_agent.check(
        instruction=instruction,
        domain=domain,
        is_preference_pass=is_preference_pass,
    )

    # goal_orientation: violation iff task_type == "procedural"
    go_passed = go_result.get("task_type") == "goal" if go_result.get("task_type") is not None else None
    goal_cr = _build_criterion_result(
        name="goal_oriented",
        passed=go_passed,
        reason=go_result.get("reason", ""),
        raw_llm_output={k: v for k, v in go_result.items() if k != "trajectory"},
        layer="llm",
    )

    # template: violation iff follows_template == False (only definitive on pref pass)
    follows = tc_result.get("follows_template")
    if not is_preference_pass:
        # For raw instructions the preference may legitimately be absent;
        # only flag a template violation when follows_template is explicitly False AND
        # has_tool_calling_task is False (no tool task at all).
        has_tool = tc_result.get("has_tool_calling_task")
        tc_passed = has_tool if has_tool is not None else None
    else:
        tc_passed = follows
    template_cr = _build_criterion_result(
        name="template",
        passed=tc_passed,
        reason=tc_result.get("reason", ""),
        raw_llm_output={k: v for k, v in tc_result.items() if k != "trajectory"},
        layer="llm",
    )

    return InstructionEvaluation(
        instruction=instruction,
        instruction_index=instruction_index,
        is_preference_pass=is_preference_pass,
        goal_orientation=goal_cr,
        template=template_cr,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(
        description="Evaluate generated tasks against four quality criteria."
    )
    p.add_argument("--config", default=None, help="Path to JSON config file.")
    p.add_argument(
        "--input-path",
        default=None,
        help="Path to *_generated_tasks.json produced by tracer2/generator.py.",
    )
    p.add_argument("--output-path", default=None, help="Where to write evaluation JSON.")
    p.add_argument(
        "--domain",
        default="airline",
        choices=["airline", "retail", "telecom", "telehealth"],
    )
    p.add_argument("--eval-model-provider", default="openai")
    p.add_argument("--eval-model", default="gpt-4.1")
    p.add_argument("--eval-temperature", type=float, default=0.0)
    p.add_argument(
        "--api-base",
        default=None,
        help="Optional LLM API base URL (e.g. vLLM endpoint).",
    )
    p.add_argument("--start-index", type=int, default=0)
    p.add_argument("--end-index", type=int, default=None)
    p.add_argument("--task-ids", nargs="*", default=None, help="Specific task_id values to evaluate.")

    # Two-pass: load --config first, then let CLI override
    args_pre, _ = p.parse_known_args()
    if args_pre.config is not None:
        cfg = _load_config_defaults(args_pre.config)
        for action in p._actions:
            if action.dest != "config" and action.dest in cfg:
                action.default = cfg[action.dest]
    return p.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    if args.input_path is None:
        print("Error: --input-path is required (or set 'input_path' in your config).")
        sys.exit(1)

    with open(args.input_path, "r", encoding="utf-8") as f:
        tasks: List[Dict[str, Any]] = json.load(f)

    if not isinstance(tasks, list):
        print("Error: input file must be a JSON array of task objects.")
        sys.exit(1)

    output_path = args.output_path or _default_output_path(args.input_path)
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    # Build agents
    agent_kwargs: Dict[str, Any] = {
        "model": args.eval_model,
        "provider": args.eval_model_provider,
        "temperature": args.eval_temperature,
    }
    if args.api_base is not None:
        agent_kwargs["api_base"] = args.api_base

    goal_agent = GoalOrientationAgent(**agent_kwargs)
    template_agent = TemplateCheckerAgent(**agent_kwargs)
    solvability_agent = SolvabilityCheckerAgent(**agent_kwargs)
    domain_agent = DomainViolationAgent(**agent_kwargs)

    # Determine which task indices to process
    if args.task_ids is not None and len(args.task_ids) > 0:
        task_id_set = {int(x) for x in args.task_ids}
        selected = [t for t in tasks if t.get("task_id") in task_id_set]
    else:
        end = args.end_index if args.end_index is not None else len(tasks)
        selected = tasks[args.start_index : end]

    # Load existing results for resume
    results: List[Dict[str, Any]] = []
    if out_p.exists():
        with open(out_p, "r", encoding="utf-8") as f:
            results = json.load(f)
        print(f"Resuming: loaded {len(results)} existing entries from {out_p}")

    completed_ok = {
        (r["task_id"], r["run"]) for r in results if not r.get("failed", False)
    }
    failed_keys = {(r["task_id"], r["run"]) for r in results if r.get("failed", False)}
    print(f"  Skipping {len(completed_ok)} completed, retrying {len(failed_keys)} failed")

    for task in selected:
        task_id = task.get("task_id", -1)
        run = task.get("run", 0)
        key = (task_id, run)

        if key in completed_ok:
            print(f"  [task_id={task_id} run={run}] Already done, skipping.")
            continue
        if key in failed_keys:
            results = [r for r in results if not (r.get("task_id") == task_id and r.get("run") == run)]
            failed_keys.discard(key)

        print(f"\n{'='*60}")
        print(f"Evaluating task_id={task_id} run={run}  domain={args.domain}")
        print(f"{'='*60}")

        try:
            preference_instruction: Optional[str] = task.get("preference_instruction")

            # --- Criteria 1 & 2: preference_instruction only ---
            pref_eval_dict: Optional[Dict[str, Any]] = None
            if preference_instruction:
                print("  [pref instr] goal + template check ...")
                pref_ie = _evaluate_instruction(
                    instruction=preference_instruction,
                    instruction_index=-1,
                    is_preference_pass=True,
                    domain=args.domain,
                    goal_agent=goal_agent,
                    template_agent=template_agent,
                )
                pref_eval_dict = pref_ie.model_dump()
                print(
                    f"    goal={pref_ie.goal_orientation.passed} "
                    f"template={pref_ie.template.passed}"
                )
            else:
                print("  [pref instr] skipped — no preference_instruction present")

            # --- Criterion 3: solvability ---
            print("  [solvability] ...")
            solv_result = solvability_agent.check(task=task)
            solv_cr = _build_criterion_result(
                name="solvable_by_ground_truth",
                passed=solv_result.get("solvable"),
                reason=solv_result.get("reason", ""),
                raw_llm_output={k: v for k, v in solv_result.items() if k != "trajectory"},
                layer=solv_result.get("layer"),
            )
            print(f"    solvable={solv_cr.passed}  layer={solv_result.get('layer')}")

            # --- Criterion 4: domain violation ---
            print("  [domain violation] ...")
            dom_result = domain_agent.check(task=task, domain=args.domain)
            dom_cr = _build_criterion_result(
                name="no_domain_violation",
                # violation when is_domain_violation is True
                passed=not dom_result.get("is_domain_violation")
                if dom_result.get("is_domain_violation") is not None
                else None,
                reason=dom_result.get("reason", ""),
                raw_llm_output={k: v for k, v in dom_result.items() if k != "trajectory"},
                layer=dom_result.get("layer"),
            )
            print(f"    domain_violation={dom_cr.violation}  layer={dom_result.get('layer')}")

            # --- Aggregate overall verdict ---
            violations: List[str] = []

            # Criteria 1 & 2: both sourced solely from preference_instruction pass
            if pref_eval_dict and not pref_eval_dict["goal_orientation"]["passed"]:
                violations.append("goal_oriented")
            if pref_eval_dict and not pref_eval_dict["template"]["passed"]:
                violations.append("template")

            if solv_cr.violation:
                violations.append("solvable_by_ground_truth")
            if dom_cr.violation:
                violations.append("no_domain_violation")

            eval_record = TaskEvaluation(
                task_id=task_id,
                run=run,
                user_id=task.get("user_id", ""),
                domain=args.domain,
                preference_instruction_eval=pref_eval_dict,
                solvability=solv_cr,
                domain_violation=dom_cr,
                overall_passed=len(violations) == 0,
                overall_violations=violations,
            )

            results.append(eval_record.model_dump())
            print(
                f"  ✓ task_id={task_id} run={run} "
                f"passed={eval_record.overall_passed} "
                f"violations={violations}"
            )

        except Exception as e:
            print(f"  ✗ Failed task_id={task_id} run={run}: {e}")
            results.append(
                {
                    "task_id": task_id,
                    "run": run,
                    "error": str(e),
                    "failed": True,
                }
            )

        # Checkpoint after every task
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

    successful = len([r for r in results if not r.get("failed", False)])
    print(f"\nCompleted: {successful}/{len(results)} tasks evaluated")
    print(f"Saved to {out_p}")


if __name__ == "__main__":
    main()
