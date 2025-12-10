import json
import os
from glob import glob

from tqdm import tqdm

OUTPUT_DIR = "output"
PATTERN = "*.json"

# which keys inside each FSP entry to visualize
FSP_VARIANTS = ["base","merged", "inserted", "miss_params", "miss_func"]


def build_mermaid_fsp(fsp, title: str):
    """
    fsp: List[Turn]
      Turn = List[item]
      item: dict with at least:
        - "type": "tool" | "missing"
        - if type == "tool": "name"
        - if type == "missing": "kind" (optional)

    Visual semantics:
      [ [A,B], [C,D], [E] ]  =>  [[A->B] -> [C->D] -> [E]]

    Implementation:
      - one subgraph per turn: Turn_0, Turn_1, ...
      - inside subgraph: chain nodes: A --> B
      - between subgraphs: last of Turn_h --> first of Turn_{h+1}
    """
    lines = []
    lines.append("```mermaid")
    lines.append("graph LR")
    lines.append(f"    %% {title}")

    node_ids_by_turn = []
    node_counter = 0

    # 1. Subgraph per turn
    for turn_idx, turn in enumerate(fsp):
        turn_node_ids = []

        # subgraph heading
        subgraph_id = f"Turn_{turn_idx}"
        # label shown on the box
        lines.append(f'    subgraph {subgraph_id} ["Turn {turn_idx}"]')
        lines.append("        direction LR")

        prev_node_id = None
        for item in turn:
            node_id = f"t{turn_idx}_n{node_counter}"
            node_counter += 1

            t = item.get("type", "tool")

            if t == "tool":
                label = item.get("name", "UNKNOWN")
            elif t == "missing":
                kind = item.get("kind", "")
                label = f"MISSING({kind})" if kind else "MISSING"
            else:
                label = "UNKNOWN"

            label = str(label).replace('"', "'")  # avoid breaking Mermaid

            # node inside this turn
            lines.append(f'        {node_id}["{label}"]')
            turn_node_ids.append(node_id)

            # chain inside the turn: A --> B
            if prev_node_id is not None:
                lines.append(f"        {prev_node_id} --> {node_id}")
            prev_node_id = node_id

        lines.append("    end")  # end subgraph
        node_ids_by_turn.append(turn_node_ids)

    # 2. Edges between turns: last of prev turn --> first of next turn
    for i in range(len(node_ids_by_turn) - 1):
        if not node_ids_by_turn[i] or not node_ids_by_turn[i + 1]:
            continue
        src = node_ids_by_turn[i][-1]
        dst = node_ids_by_turn[i + 1][0]
        # this edge visually connects the boxes: [A->B] -> [C->D]
        lines.append(f"    {src} --> {dst}")

    lines.append("```")
    return "\n".join(lines)


def main():
    # Find all JSONs under output, then keep only the fsps ones
    json_paths = sorted(
        glob(os.path.join(OUTPUT_DIR, "**", PATTERN), recursive=True)
    )
    json_paths = [p for p in json_paths if "fsps" in p]

    if not json_paths:
        raise FileNotFoundError("No FSP json files found under 'output/**/fsps/*.json'.")

    for path in tqdm(json_paths, desc="Processing FSP JSONs"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            print(f"Skipping {path}: expected a list at top-level.")
            continue

        base_name, _ = os.path.splitext(path)
        out_path = f"{base_name}_fsps_mermaid.md"

        chunks = []
        chunks.append(f"# FSP Visualizations for `{os.path.basename(path)}`\n")

        for idx, entry in enumerate(data):
            if not isinstance(entry, dict):
                continue

            chunks.append(f"\n## FSP #{idx}\n")

            for variant in FSP_VARIANTS:
                if variant not in entry:
                    continue

                fsp = entry[variant]
                title = f"FSP_{idx}_{variant}"
                mermaid = build_mermaid_fsp(fsp, title=title)

                chunks.append(f"\n### Variant: `{variant}`\n")
                chunks.append(mermaid)
                chunks.append("")  # extra newline

        content = "\n".join(chunks)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)


if __name__ == "__main__":
    main()