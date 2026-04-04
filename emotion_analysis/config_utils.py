import json
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_config(config_path: str) -> Dict[str, Any]:
    path = Path(config_path)
    if not path.is_absolute():
        path = (PROJECT_ROOT / path).resolve()
    return json.loads(path.read_text())


def resolve_project_path(path_str: str) -> str:
    path = Path(path_str)
    if not path.is_absolute():
        path = (PROJECT_ROOT / path).resolve()
    return str(path)


def ensure_parent_dir(path_str: str) -> None:
    Path(path_str).parent.mkdir(parents=True, exist_ok=True)


def ensure_dir(path_str: str) -> None:
    Path(path_str).mkdir(parents=True, exist_ok=True)
