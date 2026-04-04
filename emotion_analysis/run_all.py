import argparse

from dotenv import load_dotenv

from analyze_and_visualize import run_analysis
from config_utils import PROJECT_ROOT, ensure_dir, load_config, resolve_project_path
from encode_emotions import encode_emotions
from encode_tasks import encode_tasks


load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


def run_all(config_path: str) -> None:
    config = load_config(config_path)
    ensure_dir(resolve_project_path(config["outputs"]["root_dir"]))

    task_input = resolve_project_path(config["inputs"]["tasks_path"])
    emotion_input = resolve_project_path(config["inputs"]["emotions_path"])
    task_embeddings = resolve_project_path(config["outputs"]["task_embeddings_path"])
    emotion_embeddings = resolve_project_path(config["outputs"]["emotion_embeddings_path"])
    analysis_dir = resolve_project_path(config["outputs"]["analysis_dir"])

    encode_tasks(task_input, task_embeddings, config["encoder"])
    encode_emotions(emotion_input, emotion_embeddings, config["encoder"])
    run_analysis(task_embeddings, emotion_embeddings, analysis_dir, config.get("reranker", {}))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full pipeline using the central config.")
    parser.add_argument("--config", default="emotion_analysis/config.json", help="Path to config JSON.")
    args = parser.parse_args()
    run_all(args.config)


if __name__ == "__main__":
    main()
