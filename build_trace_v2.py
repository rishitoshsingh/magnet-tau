import argparse
import json
import os
import random
from dataclasses import asdict

import utilsv2 as utils
from utilsv2 import TRACE, Tool, load_graph_tools


def main(graph_json_path: str, num_traces: int, walk_steps: list[int]):
    if not os.path.exists(graph_json_path):
        raise FileNotFoundError(graph_json_path)
    
    tools: list[Tool] = utils.load_graph_tools(graph_json_path)
    traces: list[TRACE] = utils.build_random_walks(
        tools,
        num_walks=num_traces,
        walk_steps=walk_steps,
        rng=random.Random(42),
    )

    
    out_path = os.path.join("output","traces", os.path.basename(graph_json_path).replace(".json","_traces.json"))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    json_traces = [
        [[asdict(tool) for tool in turn] for turn in trace]
        for trace in traces
    ]

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(json_traces, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(traces)} TRACEs to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph_json_path", required=True)
    parser.add_argument("--num-traces", type=int, default=50)
    parser.add_argument("--walk-steps", nargs="+", type=int, default=[2, 3, 4])
    args = parser.parse_args()

    main(args.graph_json_path, args.num_traces, walk_steps=args.walk_steps)