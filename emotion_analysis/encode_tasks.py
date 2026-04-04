import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from config_utils import PROJECT_ROOT, ensure_parent_dir, load_config, resolve_project_path
from text_encoder import LiteLLMEncoder, SimpleEncoder


load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


def build_task_text(task: dict) -> str:
    parts = [
        task.get("instruction", ""),
        task.get("story", ""),
        " ".join(task.get("preference_instructions", []) or []),
        task.get("preference_instruction", ""),
    ]
    return "\n\n".join(part for part in parts if part)


def build_emotion_query_text(task: dict) -> str:
    feeling = task.get("feeling")
    if isinstance(feeling, str) and feeling.strip():
        return feeling.strip()
    if isinstance(feeling, list):
        parts = [str(item).strip() for item in feeling if str(item).strip()]
        if parts:
            return "\n".join(parts)
    return build_task_text(task)


def build_encoder(encoder_config: dict):
    encoder_type = encoder_config.get("type", "simple")
    if encoder_type == "simple":
        return SimpleEncoder(dim=encoder_config.get("dim", 512))
    if encoder_type == "llm":
        return LiteLLMEncoder(
            model=encoder_config["model"],
            api_base=encoder_config.get("api_base", ""),
            batch_size=encoder_config.get("batch_size", 32),
        )
    raise ValueError(f"Unsupported encoder type: {encoder_type}")


def encode_tasks(input_path: str, output_path: str, encoder_config: dict) -> None:
    tasks = json.loads(Path(input_path).read_text())
    encoder = build_encoder(encoder_config)
    raw_texts = [build_task_text(task) for task in tasks]
    emotion_query_texts = [build_emotion_query_text(task) for task in tasks]
    texts = emotion_query_texts
    vectors = encoder.encode(texts)

    records = []
    for task, raw_text, emotion_query_text, vector in zip(tasks, raw_texts, emotion_query_texts, vectors):
        records.append(
            {
                "task_id": task.get("task_id"),
                "run": task.get("run"),
                "user_id": task.get("user_id"),
                "text": emotion_query_text,
                "raw_text": raw_text,
                "emotion_query_text": emotion_query_text,
                "vector": vector.tolist(),
            }
        )

    payload = {
        "kind": "task_embeddings",
        "encoder": encoder.metadata(),
        "embedding_dim": len(records[0]["vector"]) if records else 0,
        "source_path": input_path,
        "records": records,
    }
    ensure_parent_dir(output_path)
    Path(output_path).write_text(json.dumps(payload, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Encode tasks using the central config.")
    parser.add_argument("--config", default="emotion_analysis/config.json", help="Path to config JSON.")
    args = parser.parse_args()
    config = load_config(args.config)
    encode_tasks(
        input_path=resolve_project_path(config["inputs"]["tasks_path"]),
        output_path=resolve_project_path(config["outputs"]["task_embeddings_path"]),
        encoder_config=config["encoder"],
    )


if __name__ == "__main__":
    main()
