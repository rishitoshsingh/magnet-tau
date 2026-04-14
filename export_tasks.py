f"""Export generated task JSON to a Python TASKS file.

Skips failed / incomplete generator rows (e.g. ``failed: true`` or missing ``user_id``).

Usage:
  python3 export_tasks.py input_tasks.json --package tracer2 
  python3 export_tasks.py input_tasks.json --package tracer2 --output tau-repo/package/env/domain/tasks_dev.py
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export task JSON into a Python TASKS file.")
    parser.add_argument("input_json", help="Path to task JSON list")
    parser.add_argument("--package", required=True, help="Package name used in import line: from {package}.types import Task, Action")
    parser.add_argument("--output", default=None, help="Output .py path (default: <input>.tasks.py)")
    return parser.parse_args()


def load_json(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Input JSON must be a list of task objects.")
    return data


def is_exportable_task(task: Dict[str, Any]) -> bool:
    """Exclude pipeline failures and stubs without a real user id."""
    if not isinstance(task, dict):
        return False
    if task.get("failed") is True:
        return False
    uid = task.get("user_id")
    return isinstance(uid, str) and bool(uid.strip())


def pick_instruction(task: Dict[str, Any]) -> str:
    pref = task.get("preference_instruction")
    if isinstance(pref, str) and pref.strip():
        return pref.strip()
    pref_list = task.get("preference_instructions")
    if isinstance(pref_list, list):
        for item in pref_list:
            if isinstance(item, str) and item.strip():
                return item.strip()
    inst = task.get("instruction")
    if isinstance(inst, str):
        return inst
    return ""


def pick_actions(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    actions = task.get("ground_truth_actions")
    if isinstance(actions, list):
        return actions
    actions = task.get("actions")
    if isinstance(actions, list):
        return actions
    return []


def map_task(task: Dict[str, Any]) -> Dict[str, Any]:
    instruction = pick_instruction(task)
    pred = task.get("novel_emotion_prediction", {})
    if isinstance(pred, dict):
        top2 = pred.get("closest_instructions_top2")
        if isinstance(top2, list) and len(top2) > 0 and isinstance(top2[0], dict):
            top_text = top2[0].get("text")
            if isinstance(top_text, str) and top_text.strip():
                if instruction.strip():
                    instruction = f"{instruction.strip()}\n\nEmotion instruction: {top_text.strip()}"
                else:
                    instruction = top_text.strip()

    mapped: Dict[str, Any] = {
        "user_id": task.get("user_id"),
        "instruction": instruction,
        "actions": pick_actions(task),
        "outputs": task.get("outputs", []) if isinstance(task.get("outputs", []), list) else [],
    }

    # Optional emotion fields
    if isinstance(pred, dict):
        family = pred.get("family", {}).get("label")
        leaf = pred.get("leaf", {}).get("label")
        dims = pred.get("generation_dimensions", {})
        if family:
            mapped["emotion_family"] = family
        if leaf:
            mapped["emotion_leaf"] = leaf
        if isinstance(dims, dict):
            pol = dims.get("politeness", {}).get("label")
            urg = dims.get("urgency", {}).get("label")
            trust = dims.get("trust_in_agent", {}).get("label")
            if isinstance(pol, str) and pol.strip():
                mapped["dimension_politeness"] = pol.strip()
            if isinstance(urg, str) and urg.strip():
                mapped["dimension_urgency"] = urg.strip()
            if isinstance(trust, str) and trust.strip():
                mapped["dimension_trust_in_agent"] = trust.strip()

    return mapped


def basic_validate(mapped_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    validated: List[Dict[str, Any]] = []
    for idx, row in enumerate(mapped_tasks):
        if not isinstance(row.get("user_id"), str) or not row["user_id"].strip():
            raise ValueError(f"Task {idx}: missing/invalid user_id")
        if not isinstance(row.get("instruction"), str):
            raise ValueError(f"Task {idx}: missing/invalid instruction")
        if not isinstance(row.get("actions"), list):
            raise ValueError(f"Task {idx}: actions must be a list")
        if not isinstance(row.get("outputs"), list):
            raise ValueError(f"Task {idx}: outputs must be a list")
        for j, a in enumerate(row["actions"]):
            if not isinstance(a, dict):
                raise ValueError(f"Task {idx} action {j}: action must be dict")
            if "name" not in a:
                raise ValueError(f"Task {idx} action {j}: missing action.name")
            if "kwargs" in a and not isinstance(a["kwargs"], dict):
                raise ValueError(f"Task {idx} action {j}: action.kwargs must be dict")
        validated.append(row)
    return validated


def py_literal(value: Any) -> str:
    return repr(value)


def format_task_entry(task: Dict[str, Any]) -> str:
    lines = [
        "    Task(",
        f"        user_id={py_literal(task['user_id'])},",
        f"        instruction={py_literal(task['instruction'])},",
    ]
    lines.append("        actions=[")
    for a in task.get("actions", []):
        lines.append(f"            Action(name={py_literal(a['name'])}, kwargs={py_literal(a.get('kwargs', {}))}),")
    lines.append("        ],")
    lines.append(f"        outputs={py_literal(task.get('outputs', []))},")

    optional_fields = [
        "emotion_family",
        "emotion_leaf",
        "dimension_politeness",
        "dimension_urgency",
        "dimension_trust_in_agent",
    ]
    for field in optional_fields:
        if task.get(field) is not None:
            lines.append(f"        {field}={py_literal(task[field])},")

    lines.append("    ),")
    return "\n".join(lines)


def build_py_content(package: str, tasks: List[Dict[str, Any]]) -> str:
    body = "\n\n".join(format_task_entry(t) for t in tasks)
    return (
        f"from {package}.types import Task, Action\n\n\n"
        "TASKS = [\n"
        f"{body}\n"
        "]\n"
    )


def main() -> None:
    args = parse_args()
    input_path = Path(args.input_json).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve() if args.output else input_path.with_suffix(".tasks.py")

    raw_tasks = load_json(input_path)
    n_in = len(raw_tasks)
    raw_tasks = [t for t in raw_tasks if is_exportable_task(t)]
    n_skip = n_in - len(raw_tasks)
    if n_skip:
        print(f"Skipped {n_skip} failed or incomplete task(s) (no exportable user_id).")
    if not raw_tasks:
        raise ValueError("No exportable tasks after filtering; check input JSON for failed runs.")

    mapped = [map_task(t) for t in raw_tasks]
    validated = basic_validate(mapped)
    content = build_py_content(args.package, validated)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    print(f"Wrote {output_path}")
    print(f"Exported {len(validated)} tasks")


if __name__ == "__main__":
    main()
