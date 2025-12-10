import argparse
import json
import os

from fsp_sampling import sample_enhanced_fsps_for_graph


def main(graph_json_path: str, num_fsps: int, start_tools: list[str] | None = None):
    if not os.path.exists(graph_json_path):
        raise FileNotFoundError(graph_json_path)

    fsps = sample_enhanced_fsps_for_graph(
        graph_json_path,
        num_fsps=num_fsps,
        walk_steps=5,
        p_merge=0.3,
        rng_seed=42,
        start_tools=start_tools,
    )
    out_dir = os.path.splitext(graph_json_path)[0]
    out_path = f"{out_dir}_fsps.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fsps, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(fsps)} FSPs to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph_json_path", required=True)
    parser.add_argument("--num-fsps", type=int, default=50)
    parser.add_argument("--start-tools", nargs="+", type=str, default=None)
    args = parser.parse_args()

    main(args.graph_json_path, args.num_fsps, start_tools=args.start_tools)