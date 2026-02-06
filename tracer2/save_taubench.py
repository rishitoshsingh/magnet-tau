"""Convert generated tasks JSON into a tau_bench-style Python tasks file.

This script expects two arguments:
1) Path to the generated tasks JSON (e.g., output/traces/airline_adjacency_matrix_0.0_generated_tasks.json)
2) Path to the local tau_bench repository where the tasks.py file will be written

The output will be appended to an existing tasks file in <tau_bench_path>.

- If `<tau_bench_path>/tasks_dev.py` exists, we append there.
- Else if `<tau_bench_path>/tasks.py` exists, we append there.
- Else we create `<tau_bench_path>/tasks_dev.py`.

We append into whichever variable exists in that file:
- `TASKS_DEV` if present
- else `TASKS` if present
- else we create a new list variable (matching the filename: `TASKS_DEV` for tasks_dev.py, otherwise `TASKS`).

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

If the file already exists, new tasks will be APPENDED to it without rewriting existing tasks
(so existing tasks keep their original `actions` and `outputs`).
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import tokenize


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


def _line_offsets(s: str) -> List[int]:
    """Return 0-based absolute offsets for the start of each line."""
    offs = [0]
    for i, ch in enumerate(s):
        if ch == "\n":
            offs.append(i + 1)
    return offs


def _abs_offset(line_offsets: List[int], row_1_based: int, col_0_based: int) -> int:
    return line_offsets[row_1_based - 1] + col_0_based


def _find_tasks_list_span(content: str) -> Tuple[Optional[str], Optional[Tuple[int, int]]]:
    """Find the list span for TASKS_DEV or TASKS.

    Returns (var_name, (list_start_offset, list_end_offset)) where list_start_offset points
    to the '[' token and list_end_offset points to the matching ']' token.
    """
    line_offsets = _line_offsets(content)
    tokens = tokenize.generate_tokens(iter(content.splitlines(True)).__next__)

    candidates: List[Tuple[str, Tuple[int, int]]] = []
    toks = list(tokens)
    for i, tok in enumerate(toks):
        if tok.type != tokenize.NAME or tok.string not in ("TASKS_DEV", "TASKS"):
            continue
        var_name = tok.string

        # Look for pattern: NAME '=' '['
        j = i + 1
        while j < len(toks) and toks[j].type in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT):
            j += 1
        if j >= len(toks) or toks[j].string != "=":
            continue
        j += 1
        while j < len(toks) and toks[j].type in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT):
            j += 1
        if j >= len(toks) or toks[j].string != "[":
            continue

        list_start = _abs_offset(line_offsets, toks[j].start[0], toks[j].start[1])

        depth = 0
        k = j
        end_tok = None
        while k < len(toks):
            s = toks[k].string
            if s == "[":
                depth += 1
            elif s == "]":
                depth -= 1
                if depth == 0:
                    end_tok = toks[k]
                    break
            k += 1

        if end_tok is None:
            continue
        list_end = _abs_offset(line_offsets, end_tok.start[0], end_tok.start[1])
        candidates.append((var_name, (list_start, list_end)))

    if not candidates:
        return None, None

    # Prefer TASKS_DEV if both exist.
    for name, span in candidates:
        if name == "TASKS_DEV":
            return name, span
    return candidates[0]


def _format_action(action: Dict[str, Any]) -> str:
    name = action.get("name")
    kwargs = action.get("kwargs", {})
    return f"Action(name={json.dumps(name)}, kwargs={json.dumps(kwargs)})"


def _format_task_entry(task: Dict[str, Any]) -> str:
    user_id = task.get("user_id")
    instruction = task.get("instruction")
    annotator = task.get("annotator", "0")
    actions = task.get("actions", []) or []
    outputs = task.get("outputs", []) or []

    actions_str = "[]"
    if isinstance(actions, list) and len(actions) > 0:
        actions_items = ", ".join(_format_action(a) for a in actions)
        actions_str = f"[{actions_items}]"

    # outputs is usually List[str] in tau_bench tasks
    return "\n".join(
        [
            "    Task(",
            f"        annotator={json.dumps(str(annotator))},",
            f"        user_id={json.dumps(user_id)},",
            f"        instruction={json.dumps(instruction)},",
            f"        actions={actions_str},",
            f"        outputs={json.dumps(outputs)},",
            "    ),",
        ]
    )


def _ensure_header_and_list(content: str, var_name: str) -> str:
    if content.strip() == "":
        return (
            "from tau_bench.types import Action, Task\n\n\n"
            + f"{var_name} = [\n"
            + "]\n"
        )
    if "from tau_bench.types import Action, Task" not in content:
        content = "from tau_bench.types import Action, Task\n\n" + content
    if var_name not in content:
        if not content.endswith("\n"):
            content += "\n"
        content += f"\n\n{var_name} = [\n]\n"
    return content


def write_tasks_py(content: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    tasks_json_path = Path(args.tasks_json).expanduser().resolve()
    tau_bench_path = Path(args.tau_bench_path).expanduser().resolve()
    # Prefer appending to an existing file if present.
    tasks_dev_path = tau_bench_path / "tasks_dev.py"
    tasks_path = tau_bench_path / "tasks.py"
    if tasks_dev_path.exists():
        output_path = tasks_dev_path
    elif tasks_path.exists():
        output_path = tasks_path
    else:
        output_path = tasks_dev_path

    existing_content = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
    var_name, span = _find_tasks_list_span(existing_content)
    if var_name is None:
        # Create a variable name consistent with filename if none exists.
        var_name = "TASKS_DEV" if output_path.name == "tasks_dev.py" else "TASKS"
        existing_content = _ensure_header_and_list(existing_content, var_name)
        var_name, span = _find_tasks_list_span(existing_content)
        if var_name is None or span is None:
            raise ValueError(f"Failed to create/find {var_name} list in {output_path}")

    # Load new tasks
    new_tasks = load_tasks(tasks_json_path)
    print(f"Loaded {len(new_tasks)} new tasks from {tasks_json_path}")

    # Extract fields from new tasks. If actions/outputs exist, preserve them.
    processed_tasks: List[Dict[str, Any]] = []
    for task in new_tasks:
        user_id = task.get("user_id")
        instruction = task.get("instruction")

        if not user_id or not instruction:
            print(f"Warning: Task missing user_id or instruction, skipping")
            continue

        # Use ground_truth_actions (from generator/generate_verify) or actions
        actions = task.get("actions", []) or task.get("ground_truth_actions", []) or []
        processed_tasks.append({
            "user_id": user_id,
            "instruction": instruction,
            "annotator": task.get("annotator", "0"),
            "actions": actions,
            "outputs": task.get("outputs", []) or [],
        })

    if not processed_tasks:
        print("No valid tasks to append. Exiting.")
        return

    assert span is not None
    list_start, list_end = span
    insertion_point = list_end  # insert right before the closing ']'

    new_entries = "\n\n".join(_format_task_entry(t) for t in processed_tasks)
    insert_text = ""
    # Ensure we don't end up with `[,` style formatting; just add a newline if needed.
    if existing_content[:insertion_point].rstrip().endswith("["):
        insert_text = "\n" + new_entries + "\n"
    else:
        insert_text = "\n" + new_entries + "\n"

    updated = existing_content[:insertion_point] + insert_text + existing_content[insertion_point:]
    write_tasks_py(updated, output_path)

    print(f"Appended {len(processed_tasks)} new tasks")
    print(f"Wrote to {output_path} (variable: {var_name})")


if __name__ == "__main__":
    main()
