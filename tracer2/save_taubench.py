"""Convert generated tasks JSON into a tau_bench-style Python tasks file.

This script expects two arguments:
1) Path to the generated tasks JSON (e.g., output/traces/airline_adjacency_matrix_0.0_generated_tasks.json)
2) Path to the local tau_bench repository where the tasks.py file will be written

The output will be written to <tau_bench_path>/tasks_dev.py with contents:

from tau_bench.types import Action, Task

TASKS = [
    Task(
        annotator="0",
        user_id=<user_id>,
        instruction=<instruction>,
        actions=[],
        outputs=[],
    ),
    ...
]

If the file already exists, new tasks will be APPENDED to it.
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Save generated tasks to tau_bench tasks.py (append mode)")
    parser.add_argument("tasks_json", help="Path to generated tasks JSON")
    parser.add_argument("tau_bench_path", help="Path to the local tau_bench repository")
    return parser.parse_args()


def load_tasks(tasks_json_path: Path) -> List[Dict[str, Any]]:
    with tasks_json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Tasks JSON must be a list of task objects")
    return data


def load_existing_tasks(output_path: Path) -> List[Dict[str, Any]]:
    """Load existing tasks from the file if it exists."""
    if not output_path.exists():
        return []
    
    try:
        with output_path.open("r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract user_ids and instructions from existing file
        # Pattern: user_id=("..."), instruction=("...")
        pattern = r'user_id=("(?:\\.|[^"])*"),\s*instruction=("(?:\\.|[^"])*"),'
        matches = re.findall(pattern, content)
        
        existing_tasks = []
        for match in matches:
            user_id_str = match[0]
            instruction_str = match[1]
            
            # Parse JSON strings
            user_id = json.loads(user_id_str)
            instruction = json.loads(instruction_str)
            
            existing_tasks.append({
                "user_id": user_id,
                "instruction": instruction,
            })
        
        return existing_tasks
    except Exception as e:
        print(f"Warning: Could not parse existing file: {e}")
        return []


def build_tasks_content(all_tasks: List[Dict[str, Any]]) -> str:
    """Build the complete tasks file content."""
    lines: List[str] = []
    lines.append("from tau_bench.types import Action, Task\n")
    lines.append("\n\nTASKS = [")

    for task in all_tasks:
        user_id = task.get("user_id")
        instruction = task.get("instruction")

        lines.append("    Task(")
        lines.append('        annotator="0",')
        lines.append(f"        user_id={json.dumps(user_id)},")
        lines.append(f"        instruction={json.dumps(instruction)},")
        lines.append("        actions=[],")
        lines.append("        outputs=[],")
        lines.append("    ),")

    lines.append("]\n")
    return "\n".join(lines)


def write_tasks_py(content: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    tasks_json_path = Path(args.tasks_json).expanduser().resolve()
    tau_bench_path = Path(args.tau_bench_path).expanduser().resolve()
    output_path = tau_bench_path / "tasks_dev.py"

    # Load existing tasks if file exists
    existing_tasks = load_existing_tasks(output_path)
    if existing_tasks:
        print(f"Found {len(existing_tasks)} existing tasks")

    # Load new tasks
    new_tasks = load_tasks(tasks_json_path)
    print(f"Loaded {len(new_tasks)} new tasks from {tasks_json_path}")

    # Extract user_id and instruction from new tasks
    processed_tasks = []
    for task in new_tasks:
        user_id = task.get("user_id")
        instruction = task.get("instruction")

        if not user_id or not instruction:
            print(f"Warning: Task missing user_id or instruction, skipping")
            continue

        processed_tasks.append({
            "user_id": user_id,
            "instruction": instruction,
        })

    # Combine existing and new tasks
    all_tasks = existing_tasks + processed_tasks
    
    # Build and write content
    content = build_tasks_content(all_tasks)
    write_tasks_py(content, output_path)

    print(f"Appended {len(processed_tasks)} new tasks")
    print(f"Total tasks in file: {len(all_tasks)}")
    print(f"Wrote to {output_path}")


if __name__ == "__main__":
    main()
