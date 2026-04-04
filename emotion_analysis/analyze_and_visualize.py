import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

from config_utils import PROJECT_ROOT, ensure_dir, load_config, resolve_project_path
from text_encoder import cosine_similarity, pairwise_mean_cosine_distance, pca_2d, round_float, safe_mean


load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


def load_records(path: str) -> dict:
    return json.loads(Path(path).read_text())


def to_vector(record: dict) -> np.ndarray:
    return np.array(record["vector"], dtype=float)


def compute_blend_stats(emotion_records: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for record in emotion_records:
        grouped[record["blend_id"]].append(record)

    all_vectors = [to_vector(record) for record in emotion_records]
    all_mean_similarity = []
    for i, record in enumerate(emotion_records):
        sims = []
        vector_i = all_vectors[i]
        for j, other in enumerate(emotion_records):
            if i == j:
                continue
            sims.append(cosine_similarity(vector_i, all_vectors[j]))
        all_mean_similarity.append(safe_mean(sims))

    genericness_by_instruction = {
        record["instruction_id"]: all_mean_similarity[i]
        for i, record in enumerate(emotion_records)
    }

    rows = []
    for blend_id, records in grouped.items():
        vectors = [to_vector(record) for record in records]
        centroid = np.mean(vectors, axis=0)
        rows.append(
            {
                "blend_id": blend_id,
                "category": records[0]["category"],
                "blend": " + ".join(records[0]["blend"]),
                "instruction_count": len(records),
                "mean_pairwise_distance": round_float(pairwise_mean_cosine_distance(vectors)),
                "mean_genericness": round_float(
                    safe_mean([genericness_by_instruction[record["instruction_id"]] for record in records])
                ),
                "centroid": centroid.tolist(),
            }
        )
    return rows


def build_candidate_record(score: float, emotion: dict) -> dict:
    return {
        "instruction_id": emotion["instruction_id"],
        "blend_id": emotion["blend_id"],
        "category": emotion["category"],
        "blend": " + ".join(emotion["blend"]),
        "similarity": round_float(score),
        "instruction_text": emotion["instruction_text"],
    }


def rerank_candidates_with_llm(task: dict, candidates: list[dict], reranker_config: dict) -> list[dict]:
    if not candidates:
        return candidates

    try:
        from litellm import completion
    except ImportError as exc:
        raise ImportError("litellm is required when reranker.enabled=true.") from exc

    candidate_lines = []
    for index, candidate in enumerate(candidates, start=1):
        candidate_lines.append(
            f"{index}. id={candidate['instruction_id']} | blend={candidate['blend']} | text={candidate['instruction_text']}"
        )

    prompt = f"""You are ranking emotion instructions for a customer task.

Customer feeling:
{task.get('emotion_query_text', task.get('text', ''))}

Task context:
{task.get('raw_text', task.get('text', ''))}

Candidates:
{chr(10).join(candidate_lines)}

Return JSON with this schema:
{{
  "ranking": [instruction_id_1, instruction_id_2, instruction_id_3]
}}

Rules:
- Rank only from the provided candidate instruction ids.
- Rank by best emotional fit for the customer feeling.
- Prefer the instruction that most closely matches the feeling description, not the task logistics.
- Return valid JSON only.
"""

    kwargs = {
        "model": reranker_config["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    if reranker_config.get("api_base"):
        kwargs["api_base"] = reranker_config["api_base"]

    response = completion(**kwargs)
    content = response["choices"][0]["message"]["content"]
    payload = json.loads(content)
    ranked_ids = payload.get("ranking", [])
    if not isinstance(ranked_ids, list):
        return candidates

    by_id = {candidate["instruction_id"]: candidate for candidate in candidates}
    reranked = [by_id[instruction_id] for instruction_id in ranked_ids if instruction_id in by_id]
    seen = {candidate["instruction_id"] for candidate in reranked}
    reranked.extend(candidate for candidate in candidates if candidate["instruction_id"] not in seen)
    return reranked


def rank_instructions_for_tasks(task_records: list[dict], emotion_records: list[dict], reranker_config: Optional[dict] = None) -> list[dict]:
    rankings = []
    use_reranker = bool(reranker_config and reranker_config.get("enabled"))

    for task in tqdm(task_records, desc="Ranking tasks", unit="task"):
        task_vector = to_vector(task)
        scores = []
        for emotion in emotion_records:
            emotion_vector = to_vector(emotion)
            score = cosine_similarity(task_vector, emotion_vector)
            scores.append((score, emotion))

        scores.sort(key=lambda item: item[0], reverse=True)
        top_k = reranker_config.get("top_k", 5) if reranker_config else 5
        retrieved_candidates = [build_candidate_record(score, emotion) for score, emotion in scores[:top_k]]
        ranked_candidates = retrieved_candidates
        selection_method = "embedding"
        if use_reranker:
            ranked_candidates = rerank_candidates_with_llm(task, retrieved_candidates, reranker_config)
            selection_method = "reranker"

        top_candidate = ranked_candidates[0]
        second_candidate = ranked_candidates[1] if len(ranked_candidates) > 1 else None
        top_score = top_candidate["similarity"]
        second_score = second_candidate["similarity"] if second_candidate else 0.0
        top_candidates = ranked_candidates[:3]

        rankings.append(
            {
                "task_id": task["task_id"],
                "run": task["run"],
                "user_id": task["user_id"],
                "selection_method": selection_method,
                "best_instruction_id": top_candidate["instruction_id"],
                "best_blend_id": top_candidate["blend_id"],
                "best_category": top_candidate["category"],
                "best_blend": top_candidate["blend"],
                "similarity": round_float(top_score),
                "confidence_margin": round_float(top_score - second_score),
                "instruction_text": top_candidate["instruction_text"],
                "task_text": task["text"],
                "raw_task_text": task.get("raw_text", task["text"]),
                "emotion_query_text": task.get("emotion_query_text", task["text"]),
                "top_1_instruction_id": top_candidates[0]["instruction_id"] if len(top_candidates) > 0 else "",
                "top_1_blend": top_candidates[0]["blend"] if len(top_candidates) > 0 else "",
                "top_1_similarity": top_candidates[0]["similarity"] if len(top_candidates) > 0 else 0.0,
                "top_2_instruction_id": top_candidates[1]["instruction_id"] if len(top_candidates) > 1 else "",
                "top_2_blend": top_candidates[1]["blend"] if len(top_candidates) > 1 else "",
                "top_2_similarity": top_candidates[1]["similarity"] if len(top_candidates) > 1 else 0.0,
                "top_3_instruction_id": top_candidates[2]["instruction_id"] if len(top_candidates) > 2 else "",
                "top_3_blend": top_candidates[2]["blend"] if len(top_candidates) > 2 else "",
                "top_3_similarity": top_candidates[2]["similarity"] if len(top_candidates) > 2 else 0.0,
            }
        )
    return rankings


def build_plot_rows(task_records: list[dict], emotion_records: list[dict], rankings: list[dict]) -> list[dict]:
    matrix = []
    rows = []

    for emotion in emotion_records:
        matrix.append(to_vector(emotion))
        rows.append(
            {
                "kind": "emotion",
                "label": emotion["instruction_id"],
                "group": emotion["category"],
                "blend": " + ".join(emotion["blend"]),
            }
        )

    ranking_map = {row["task_id"]: row for row in rankings}
    for task in task_records:
        matrix.append(to_vector(task))
        best = ranking_map[task["task_id"]]
        rows.append(
            {
                "kind": "task",
                "label": f"task_{task['task_id']}",
                "group": best["best_category"],
                "blend": best["best_blend"],
            }
        )

    points = pca_2d(np.vstack(matrix))
    for row, point in zip(rows, points):
        row["x"] = round_float(point[0], 6)
        row["y"] = round_float(point[1], 6)
    return rows


def write_html_plot(plot_rows: list[dict], output_path: str) -> None:
    if not plot_rows:
        Path(output_path).write_text("<html><body><p>No points to plot.</p></body></html>")
        return

    xs = [row["x"] for row in plot_rows]
    ys = [row["y"] for row in plot_rows]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    def scale(value: float, low: float, high: float, out_low: float, out_high: float) -> float:
        if high == low:
            return (out_low + out_high) / 2
        ratio = (value - low) / (high - low)
        return out_low + ratio * (out_high - out_low)

    colors = {
        "happy": "#f28e2b",
        "scared": "#4e79a7",
        "sad": "#9c755f",
        "angry": "#e15759",
        "calm": "#59a14f",
    }

    circles = []
    labels = []
    for row in plot_rows:
        cx = scale(row["x"], min_x, max_x, 70, 1130)
        cy = scale(row["y"], min_y, max_y, 650, 70)
        color = colors.get(str(row["group"]).lower(), "#777777")
        radius = 5 if row["kind"] == "emotion" else 3.5
        opacity = 0.85 if row["kind"] == "emotion" else 0.45
        circles.append(
            f"<circle cx='{cx:.2f}' cy='{cy:.2f}' r='{radius}' fill='{color}' opacity='{opacity}'>"
            f"<title>{row['label']} | {row['blend']}</title></circle>"
        )
        if row["kind"] == "emotion":
            labels.append(
                f"<text x='{cx + 7:.2f}' y='{cy - 6:.2f}' font-size='10' fill='#222'>{row['blend']}</text>"
            )

    legend = []
    y = 40
    for name, color in colors.items():
        legend.append(f"<circle cx='980' cy='{y}' r='6' fill='{color}'></circle>")
        legend.append(f"<text x='995' y='{y + 4}' font-size='12'>{name}</text>")
        y += 24

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Emotion Task Embedding Plot</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #222; }}
    .note {{ color: #555; max-width: 900px; }}
    svg {{ border: 1px solid #ddd; background: #fff; }}
  </style>
</head>
<body>
  <h1>Task and Emotion Instruction Embedding Plot</h1>
  <p class="note">This is a simple 2D PCA projection of hashed text vectors. Larger points are emotion instructions. Smaller points are tasks colored by the category of their top-matched instruction.</p>
  <svg width="1200" height="720" viewBox="0 0 1200 720">
    <rect x="0" y="0" width="1200" height="720" fill="#faf9f7"></rect>
    {''.join(circles)}
    {''.join(labels[:80])}
    {''.join(legend)}
  </svg>
</body>
</html>"""
    Path(output_path).write_text(html)


def run_analysis(task_embeddings_path: str, emotion_embeddings_path: str, output_dir: str, reranker_config: Optional[dict] = None) -> None:
    output = Path(output_dir)
    ensure_dir(str(output))

    task_payload = load_records(task_embeddings_path)
    emotion_payload = load_records(emotion_embeddings_path)
    task_records = task_payload["records"]
    emotion_records = emotion_payload["records"]

    blend_stats = compute_blend_stats(emotion_records)
    rankings = rank_instructions_for_tasks(task_records, emotion_records, reranker_config=reranker_config)
    plot_rows = build_plot_rows(task_records, emotion_records, rankings)

    blend_stats_csv = output / "blend_stats.csv"
    rankings_csv = output / "task_to_instruction_rankings.csv"
    plot_json = output / "plot_points.json"
    plot_html = output / "embedding_plot.html"
    summary_json = output / "summary.json"

    pd.DataFrame([{k: v for k, v in row.items() if k != "centroid"} for row in blend_stats]).to_csv(blend_stats_csv, index=False)
    pd.DataFrame(rankings).to_csv(rankings_csv, index=False)
    plot_json.write_text(json.dumps(plot_rows, indent=2))
    write_html_plot(plot_rows, str(plot_html))

    summary = {
        "task_count": len(task_records),
        "emotion_instruction_count": len(emotion_records),
        "blend_count": len(blend_stats),
        "average_top_similarity": round_float(safe_mean([row["similarity"] for row in rankings])),
        "reranker_enabled": bool(reranker_config and reranker_config.get("enabled")),
        "outputs": {
            "blend_stats_csv": str(blend_stats_csv),
            "rankings_csv": str(rankings_csv),
            "plot_json": str(plot_json),
            "plot_html": str(plot_html),
        },
    }
    summary_json.write_text(json.dumps(summary, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze embeddings using the central config.")
    parser.add_argument("--config", default="emotion_analysis/config.json", help="Path to config JSON.")
    args = parser.parse_args()
    config = load_config(args.config)
    run_analysis(
        task_embeddings_path=resolve_project_path(config["outputs"]["task_embeddings_path"]),
        emotion_embeddings_path=resolve_project_path(config["outputs"]["emotion_embeddings_path"]),
        output_dir=resolve_project_path(config["outputs"]["analysis_dir"]),
        reranker_config=config.get("reranker", {}),
    )


if __name__ == "__main__":
    main()
