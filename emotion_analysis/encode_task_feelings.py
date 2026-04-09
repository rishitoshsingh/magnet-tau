import argparse
import json
from typing import Dict, List

import numpy as np

from utils import (
    cosine_similarity,
    encode_texts,
    format_task_skip_line,
    get_embedding_model_cfg,
    l2_normalize_rows,
    load_config,
    load_encoder_knn_models,
    output_dir_for_model,
    resolve_project_path,
    task_embedding_text,
)


def _invert_map(mapping: Dict[str, int]) -> Dict[int, str]:
    return {int(v): k for k, v in mapping.items()}


def select_torch_device(torch_module) -> str:
    if torch_module.cuda.is_available():
        return "cuda"
    if hasattr(torch_module.backends, "mps") and torch_module.backends.mps.is_available():
        return "mps"
    return "cpu"


def predict_for_model(config: Dict, model_cfg: Dict) -> Dict[str, str]:
    try:
        import torch
        import torch.nn as nn
        import torch.nn.functional as F
    except ImportError as exc:
        raise ImportError("PyTorch is required. Install torch in your environment.") from exc

    model_dir = output_dir_for_model(config, model_cfg)
    label_maps = json.loads((model_dir / "label_maps.json").read_text(encoding="utf-8"))
    train_meta = json.loads((model_dir / "training_metadata.json").read_text(encoding="utf-8"))
    emotions_payload = json.loads((model_dir / "emotion_embeddings.json").read_text(encoding="utf-8"))

    family_from_idx = _invert_map(label_maps["family_to_idx"])
    leaf_from_idx = _invert_map(label_maps["leaf_to_idx"])
    dim_from_idx = {dim: _invert_map(class_map) for dim, class_map in label_maps["dim_to_idx"].items()}

    input_dim = int(train_meta["input_dim"])
    hidden_dim = int(train_meta["hidden_dim"])
    dropout = float(train_meta["dropout"])

    class MultiHeadModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.backbone = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),
            )
            self.family_head = nn.Linear(hidden_dim, len(label_maps["family_to_idx"]))
            self.leaf_head = nn.Linear(hidden_dim, len(label_maps["leaf_to_idx"]))
            self.dim_heads = nn.ModuleDict({
                dim: nn.Linear(hidden_dim, len(class_map)) for dim, class_map in label_maps["dim_to_idx"].items()
            })

        def forward(self, features):
            z = self.backbone(features)
            out = {"family": self.family_head(z), "leaf": self.leaf_head(z)}
            for dim_name, head in self.dim_heads.items():
                out[dim_name] = head(z)
            return out

    model = MultiHeadModel()
    device = select_torch_device(torch)
    try:
        w = torch.load(model_dir / "trained_encoder.pt", map_location=torch.device(device), weights_only=True)
    except TypeError:
        w = torch.load(model_dir / "trained_encoder.pt", map_location=torch.device(device))
    model.load_state_dict(w)
    model = model.to(device)
    model.eval()
    knn_models = load_encoder_knn_models(model_dir)
    if knn_models:
        print(f"Inference device: {device} (task labels: backbone + kNN)")
    else:
        print(f"Inference device: {device} (task labels: classifier heads; no knn_models.pt)")

    emotion_vectors = np.array([row["vector"] for row in emotions_payload["records"]], dtype=float)
    emotion_rows = emotions_payload["records"]

    output_suffix = config["inference"].get("task_output_suffix", "_with_novel_emotion_predictions.json")
    written_paths: List[str] = []
    for task_path_str in config["inputs"]["task_paths"]:
        task_path = resolve_project_path(task_path_str)
        tasks = json.loads(task_path.read_text(encoding="utf-8"))
        encode_indices: List[int] = []
        texts: List[str] = []
        for i, task in enumerate(tasks):
            t = task_embedding_text(task)
            if not str(t).strip():
                print(format_task_skip_line(task_path, i, task))
                continue
            encode_indices.append(i)
            texts.append(t)

        if not encode_indices:
            print(f"No tasks to encode in {task_path} (all skipped); writing copy without novel_emotion_prediction.")
        else:
            vectors = encode_texts(model_cfg, texts).astype(np.float32)
            vt = torch.tensor(vectors, device=device)

            if knn_models:
                with torch.no_grad():
                    z = model.backbone(vt).detach().cpu().numpy().astype(np.float32)
                z_n = l2_normalize_rows(z)
                fam_clf = knn_models["family"]
                leaf_clf = knn_models["leaf"]
                fam_probs = np.stack([fam_clf.predict_proba(z_n[j : j + 1])[0] for j in range(len(z_n))])
                leaf_probs = np.stack([leaf_clf.predict_proba(z_n[j : j + 1])[0] for j in range(len(z_n))])
                dim_probs = {}
                for dim_name in dim_from_idx:
                    clf = knn_models[dim_name]
                    dim_probs[dim_name] = np.stack(
                        [clf.predict_proba(z_n[j : j + 1])[0] for j in range(len(z_n))]
                    )
            else:
                with torch.no_grad():
                    outputs = model(vt)
                    fam_probs = F.softmax(outputs["family"], dim=1).detach().cpu().numpy()
                    leaf_probs = F.softmax(outputs["leaf"], dim=1).detach().cpu().numpy()
                    dim_probs = {
                        dim: F.softmax(logits, dim=1).detach().cpu().numpy()
                        for dim, logits in outputs.items()
                        if dim not in ("family", "leaf")
                    }

            for j, orig_i in enumerate(encode_indices):
                task = tasks[orig_i]
                if knn_models:
                    fc, lc = knn_models["family"], knn_models["leaf"]
                    fi = int(np.argmax(fam_probs[j]))
                    family_idx = int(fc.classes_[fi])
                    li = int(np.argmax(leaf_probs[j]))
                    leaf_idx = int(lc.classes_[li])
                    dims = {}
                    for dim_name, probs in dim_probs.items():
                        clf = knn_models[dim_name]
                        pr = probs[j]
                        bi = int(np.argmax(pr))
                        idx = int(clf.classes_[bi])
                        dmap = dim_from_idx[dim_name]
                        dims[dim_name] = {
                            "label": dmap[idx],
                            "score": float(pr[bi]),
                            "distribution": {
                                dmap[int(c)]: float(p) for c, p in zip(clf.classes_, pr)
                            },
                        }
                else:
                    family_idx = int(np.argmax(fam_probs[j]))
                    leaf_idx = int(np.argmax(leaf_probs[j]))
                    dims = {}
                    for dim_name, probs in dim_probs.items():
                        idx = int(np.argmax(probs[j]))
                        dims[dim_name] = {
                            "label": dim_from_idx[dim_name][idx],
                            "score": float(probs[j][idx]),
                            "distribution": {
                                dim_from_idx[dim_name][k]: float(probs[j][k])
                                for k in range(probs.shape[1])
                            },
                        }

                task_vec = vectors[j].astype(float)
                sims = []
                for row, emo_vec in zip(emotion_rows, emotion_vectors):
                    sims.append((cosine_similarity(task_vec, emo_vec), row))
                sims.sort(key=lambda x: x[0], reverse=True)
                top2 = sims[:2]

                if knn_models:
                    fc, lc = knn_models["family"], knn_models["leaf"]
                    fi = int(np.argmax(fam_probs[j]))
                    li = int(np.argmax(leaf_probs[j]))
                    fam_dist = {
                        family_from_idx[int(c)]: float(p)
                        for c, p in zip(fc.classes_, fam_probs[j])
                    }
                    leaf_dist = {
                        leaf_from_idx[int(c)]: float(p)
                        for c, p in zip(lc.classes_, leaf_probs[j])
                    }
                    fam_block = {
                        "label": family_from_idx[family_idx],
                        "score": float(fam_probs[j][fi]),
                        "distribution": fam_dist,
                    }
                    leaf_block = {
                        "label": leaf_from_idx[leaf_idx],
                        "score": float(leaf_probs[j][li]),
                        "distribution": leaf_dist,
                    }
                else:
                    fam_block = {
                        "label": family_from_idx[family_idx],
                        "score": float(fam_probs[j][family_idx]),
                        "distribution": {
                            family_from_idx[k]: float(fam_probs[j][k])
                            for k in range(fam_probs.shape[1])
                        },
                    }
                    leaf_block = {
                        "label": leaf_from_idx[leaf_idx],
                        "score": float(leaf_probs[j][leaf_idx]),
                        "distribution": {
                            leaf_from_idx[k]: float(leaf_probs[j][k])
                            for k in range(leaf_probs.shape[1])
                        },
                    }

                task["novel_emotion_prediction"] = {
                    "family": fam_block,
                    "leaf": leaf_block,
                    "generation_dimensions": dims,
                    "closest_instructions_top2": [
                        {
                            "instruction_id": row["instruction_id"],
                            "item_id": row["item_id"],
                            "similarity": float(score),
                            "text": row["instruction_text"],
                        }
                        for score, row in top2
                    ],
                }

        skipped_n = len(tasks) - len(encode_indices)
        if skipped_n:
            print(f"Skipped {skipped_n} task(s) in {task_path.name} (no embedding; no novel_emotion_prediction).")

        out_path = task_path.with_name(f"{task_path.stem}{output_suffix}")
        out_path.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
        written_paths.append(str(out_path))
        print(f"Wrote {out_path}")

    summary_path = model_dir / "task_prediction_outputs.json"
    summary_path.write_text(json.dumps({"outputs": written_paths}, indent=2), encoding="utf-8")
    return {"summary_path": str(summary_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Encode task feelings and run trained novel emotion encoder.")
    parser.add_argument("--config", default="emotion_analysis/config.json")
    args = parser.parse_args()

    config = load_config(args.config)
    model_cfg = get_embedding_model_cfg(config)
    result = predict_for_model(config, model_cfg)
    print(f"Wrote {result['summary_path']}")


if __name__ == "__main__":
    main()
