import json
import sys
from pathlib import Path
from typing import Optional

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

VIEWER_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = VIEWER_DIR.parent

_loaded_tasks = None
_loaded_path = None


def _resolve_path(path_str: str) -> Path:
    raw_path = path_str.strip()
    if not raw_path:
        raise ValueError("Path is empty.")

    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = (PROJECT_ROOT / candidate).resolve()
    else:
        candidate = candidate.resolve()

    if not candidate.is_file():
        raise FileNotFoundError(f"File not found: {candidate}")

    try:
        candidate.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise ValueError("Path must stay inside the project root.") from exc

    return candidate


def load_tasks(path_str: str) -> list[dict]:
    global _loaded_tasks, _loaded_path

    path = _resolve_path(path_str)
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise ValueError("JSON root must be an array.")

    _loaded_tasks = data
    _loaded_path = str(path)
    return data


def _preview(text: Optional[str], limit: int = 160) -> str:
    if not text:
        return ""
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[:limit].rstrip()}..."


def _message_preview(message: dict, limit: int = 100) -> str:
    content = message.get("content")
    if isinstance(content, list):
        content = json.dumps(content, ensure_ascii=False)
    if not isinstance(content, str):
        content = str(content or "")
    return _preview(content, limit)


def _enrich_task(task: dict, index: int) -> dict:
    task_copy = dict(task)
    task_copy["_index"] = index
    task_copy["_instruction_preview"] = _preview(task.get("instruction") or "")
    task_copy["_trajectory_groups"] = [
        {
            "label": "Generator trajectory",
            "key": "generator_traj",
            "messages": task.get("generator_traj") or [],
        },
        {
            "label": "Preference trajectory",
            "key": "preference_traj",
            "messages": task.get("preference_traj") or [],
        },
        {
            "label": "Feeling generator trajectory",
            "key": "feeling_traj",
            "messages": task.get("feeling_traj") or [],
        },
        {
            "label": "Task checker trajectory",
            "key": "task_checker_traj",
            "messages": task.get("task_checker_traj") or [],
        },
    ]
    task_copy["_feeling_preview"] = _preview(task.get("feeling") or "")
    return task_copy


@app.route("/")
def index():
    path_param = (request.args.get("path") or "").strip()
    error = None

    if path_param:
        try:
            load_tasks(path_param)
        except Exception as exc:
            error = str(exc)

    tasks = None
    if _loaded_tasks is not None:
        tasks = [_enrich_task(task, index) for index, task in enumerate(_loaded_tasks)]

    return render_template(
        "index.html",
        error=error,
        path_tried=path_param,
        tasks=tasks,
        loaded_path=_loaded_path,
        message_preview=_message_preview,
    )


@app.route("/load", methods=["POST"])
def load_path():
    path_param = (request.form.get("path") or "").strip()
    if not path_param:
        return redirect(url_for("index"))
    return redirect(url_for("index", path=path_param))


def main():
    if len(sys.argv) > 1:
        load_tasks(sys.argv[1])
    app.run(debug=True, port=5000)


if __name__ == "__main__":
    main()
