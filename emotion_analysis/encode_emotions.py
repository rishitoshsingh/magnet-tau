import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from config_utils import PROJECT_ROOT, ensure_parent_dir, load_config, resolve_project_path
from text_encoder import LiteLLMEncoder, SimpleEncoder


load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


def build_instruction_text(category: str, blend: dict, instruction: dict) -> str:
    blend_terms = ", ".join(blend.get("blend", []))
    parts = [
        f"Category: {category}",
        f"Blend: {blend_terms}",
        f"Rationale: {blend.get('rationale', '')}",
        f"Instruction: {instruction.get('text', '')}",
    ]
    return "\n".join(parts)


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


def encode_emotions(input_path: str, output_path: str, encoder_config: dict) -> None:
    data = json.loads(Path(input_path).read_text())
    encoder = build_encoder(encoder_config)

    items = []
    texts = []
    for category in data.get("categories", []):
        category_name = category.get("category")
        for blend in category.get("blends", []):
            for instruction in blend.get("instructions", []):
                text = build_instruction_text(category_name, blend, instruction)
                items.append((category_name, blend, instruction, text))
                texts.append(text)

    vectors = encoder.encode(texts)
    records = []
    for item, vector in zip(items, vectors):
        category_name, blend, instruction, text = item
        records.append(
            {
                "category": category_name,
                "blend_id": blend.get("id"),
                "blend": blend.get("blend", []),
                "rationale": blend.get("rationale", ""),
                "instruction_id": instruction.get("id"),
                "instruction_text": instruction.get("text", ""),
                "text": text,
                "vector": vector.tolist(),
            }
        )

    payload = {
        "kind": "emotion_embeddings",
        "encoder": encoder.metadata(),
        "embedding_dim": len(records[0]["vector"]) if records else 0,
        "source_path": input_path,
        "records": records,
    }
    ensure_parent_dir(output_path)
    Path(output_path).write_text(json.dumps(payload, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Encode emotion instructions using the central config.")
    parser.add_argument("--config", default="emotion_analysis/config.json", help="Path to config JSON.")
    args = parser.parse_args()
    config = load_config(args.config)
    encode_emotions(
        input_path=resolve_project_path(config["inputs"]["emotions_path"]),
        output_path=resolve_project_path(config["outputs"]["emotion_embeddings_path"]),
        encoder_config=config["encoder"],
    )


if __name__ == "__main__":
    main()
