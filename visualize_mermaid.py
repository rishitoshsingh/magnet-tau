import glob
import json
import os
import re

OUTPUT_DIR = "output"
PATTERN = "*.json"   # adjust if needed

# Toggle this if you *really* want edge text.
# Start with False to verify everything works, then try True.
INCLUDE_EDGE_LABELS = False

MAX_EDGE_LABEL_LEN = 50
MAX_NODE_LABEL_LEN = 40


def sanitize_node_label(label: str, max_len: int) -> str:
    """Safe-ish label for node text."""
    if not label:
        return ""

    # Remove newlines, normalize whitespace
    label = label.replace("\r", " ").replace("\n", " ")
    label = re.sub(r"\s+", " ", label).strip()

    # Strip nasty stuff but keep basic punctuation
    label = re.sub(r"[^A-Za-z0-9 ._/-]", "", label)

    if len(label) > max_len:
        label = label[:max_len] + "…"
    return label


def sanitize_edge_label(label: str, max_len: int) -> str:
    """
    Make a label *very* safe for Mermaid edge text.
    Only allow letters, digits, spaces, dot, underscore, hyphen.
    No pipes, no brackets, no commas, no weird unicode.
    """
    if not label:
        return ""

    label = label.replace("\r", " ").replace("\n", " ")
    label = re.sub(r"\s+", " ", label).strip()

    # Only super-safe chars
    label = re.sub(r"[^A-Za-z0-9 ._-]", "", label)

    if len(label) > max_len:
        label = label[:max_len] + "…"
    return label


def load_graph_data(path: str):
    """
    Load tools, adjacency_matrix, reason_matrix from a JSON file,
    handling common wrapper shapes and triple-nested matrices.
    """
    with open(path, "r") as f:
        data = json.load(f)

    # Case 1: top-level list -> pick first dict with 'tools' & 'adjacency_matrix'
    if isinstance(data, list):
        candidate = None
        for item in data:
            if isinstance(item, dict) and "tools" in item and "adjacency_matrix" in item:
                candidate = item
                break
        if candidate is None:
            raise ValueError("Top-level is list but no item with 'tools' & 'adjacency_matrix'.")
        data = candidate

    # Case 2: wrapper like {"results": {...}}
    if isinstance(data, dict) and "results" in data and "tools" not in data:
        data = data["results"]

    if not isinstance(data, dict):
        raise ValueError("Unsupported JSON shape (not dict after normalization).")

    if "tools" not in data or "adjacency_matrix" not in data:
        raise ValueError("JSON lacks 'tools' or 'adjacency_matrix' keys.")

    tools = data["tools"]
    adjacency_matrix = data["adjacency_matrix"]
    reason_matrix = data.get("reason_matrix")

    # Unwrap triple nesting: [ [ [x, ...] ], ... ] -> [ [x, ...], ... ]
    def unwrap_matrix(mat):
        if mat is None:
            return None
        cleaned = []
        for row in mat:
            if isinstance(row, list) and row and isinstance(row[0], list):
                cleaned.append(row[0])
            else:
                cleaned.append(row)
        return cleaned

    adjacency_matrix = unwrap_matrix(adjacency_matrix)
    reason_matrix = unwrap_matrix(reason_matrix)

    return tools, adjacency_matrix, reason_matrix


def to_mermaid(tools, adjacency_matrix, reason_matrix, direction: str = "LR") -> str:
    """
    Convert graph data into a Mermaid 'graph LR' string.
    """
    tool_names = [t["name"] for t in tools]
    n_tools = len(tool_names)

    # Map each tool name to a simple node id for Mermaid
    id_map = {name: f"n{i}" for i, name in enumerate(tool_names)}

    lines = [f"graph {direction}"]

    # Nodes
    for name, node_id in id_map.items():
        label = sanitize_node_label(str(name), MAX_NODE_LABEL_LEN)
        lines.append(f'  {node_id}["{label}"]')

    if not adjacency_matrix:
        return "\n".join(lines)

    # Edges
    n_rows = min(len(adjacency_matrix), n_tools)
    for i in range(n_rows):
        row = adjacency_matrix[i]
        if row is None:
            continue

        n_cols = min(len(row), n_tools)
        for j in range(n_cols):
            flag = row[j]
            if not flag:
                continue

            src_name = tool_names[i]
            dst_name = tool_names[j]
            src_id = id_map[src_name]
            dst_id = id_map[dst_name]

            if INCLUDE_EDGE_LABELS:
                label = ""
                if reason_matrix is not None and i < len(reason_matrix):
                    r_row = reason_matrix[i]
                    if r_row is not None and j < len(r_row):
                        label = (r_row[j] or "").strip()

                label = sanitize_edge_label(label, MAX_EDGE_LABEL_LEN)

                if label:
                    # label is guaranteed not to contain '|'
                    lines.append(f'  {src_id} -->|{label}| {dst_id}')
                else:
                    lines.append(f"  {src_id} --> {dst_id}")
            else:
                # No labels at all – safest possible
                lines.append(f"  {src_id} --> {dst_id}")

    return "\n".join(lines)


def main():
    json_paths = sorted(
        glob.glob(os.path.join(OUTPUT_DIR, "**", PATTERN), recursive=True)
    )

    if not json_paths:
        print(f"No JSON files found in {OUTPUT_DIR}")
        return

    for path in json_paths:
        basename = os.path.splitext(path)[0]
        md_name = f"{basename}_graph.md"
        print(f"Processing {path} -> {md_name}")

        try:
            tools, adjacency_matrix, reason_matrix = load_graph_data(path)
            mermaid_src = to_mermaid(tools, adjacency_matrix, reason_matrix, direction="LR")

            md_content = f"""```mermaid
{mermaid_src}
```"""

            with open(md_name, "w", encoding="utf-8") as f:
                f.write(md_content)
        except Exception as e:
            print(f"Failed to process {path}: {e}")


if __name__ == "__main__":
    main()