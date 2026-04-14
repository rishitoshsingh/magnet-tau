import json
import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

VIEWER_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = VIEWER_DIR.parent
TASKS_DIR = PROJECT_ROOT / "output" / "tasks"
COUNTERS_FILE = VIEWER_DIR / ".counters.json"


def _preview(text: str, limit: int = 90) -> str:
    if not text:
        return ""
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[:limit].rstrip()}..."


def load_all_files(tasks_dir: Path) -> dict:
    """Return {filename: {task_id: {run: task_dict}}}."""
    result = {}
    for json_file in sorted(tasks_dir.glob("*.json")):
        if json_file.name.startswith("."):
            continue
        try:
            with json_file.open(encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, list) or not data:
                continue
            # Must look like task objects
            if not isinstance(data[0], dict) or "task_id" not in data[0]:
                continue
            grouped: dict = {}
            for task in data:
                tid = task.get("task_id", 0)
                run = task.get("run", 0)
                if tid not in grouped:
                    grouped[tid] = {}
                # Attach a preview so templates don't do heavy work
                task["_instruction_preview"] = _preview(task.get("instruction") or "")
                task["_feeling_preview"] = _preview(task.get("feeling") or "", 60)
                grouped[tid][run] = task
            result[json_file.name] = grouped
        except Exception:
            continue
    return result


def load_counters() -> dict:
    if COUNTERS_FILE.exists():
        try:
            return json.loads(COUNTERS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


@app.route("/")
def index():
    dir_param = request.args.get("dir", "").strip()
    error = None
    active_dir = TASKS_DIR

    if dir_param:
        candidate = Path(dir_param).expanduser().resolve()
        if not candidate.is_dir():
            error = f"Directory not found: {candidate}"
        else:
            active_dir = candidate

    files = load_all_files(active_dir)
    counters = load_counters()
    return render_template(
        "index.html",
        files=files,
        counters_json=json.dumps(counters),
        tasks_dir=str(active_dir),
        dir_param=dir_param,
        error=error,
    )


@app.route("/save", methods=["POST"])
def save():
    data = request.get_json(silent=True) or {}
    COUNTERS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return jsonify(ok=True)


def main():
    global TASKS_DIR
    if len(sys.argv) > 1:
        TASKS_DIR = Path(sys.argv[1]).expanduser().resolve()
    app.run(debug=True, port=5000)


if __name__ == "__main__":
    main()
