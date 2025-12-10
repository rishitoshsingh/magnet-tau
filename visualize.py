import glob
import json
import os

import networkx as nx
from pyvis.network import Network

OUTPUT_DIR = "output"
PATTERN = "*.json"   # adjust if needed


def build_graph_from_json(path: str) -> nx.DiGraph:
    with open(path, "r") as f:
        data = json.load(f)

    # If your JSON has a "results" wrapper, uncomment this and adjust:
    # data = data["results"]

    tools = data["tools"]
    adjacency_matrix = data["adjacency_matrix"]
    reason_matrix = data.get("reason_matrix")

    tool_names = [t["name"] for t in tools]
    n_tools = len(tool_names)

    # ---- unwrap triple nesting: [ [ [bool, ...] ], ... ] -> [ [bool, ...], ... ] ----
    cleaned_adj = []
    for row in adjacency_matrix:
        # row is like: [ [false, true, ...] ]
        if isinstance(row, list) and len(row) > 0 and isinstance(row[0], list):
            cleaned_adj.append(row[0])
        else:
            cleaned_adj.append(row)
    adjacency_matrix = cleaned_adj

    if reason_matrix is not None:
        cleaned_reason = []
        for row in reason_matrix:
            # row is like: [ ["reason1", "reason2", ...] ]
            if isinstance(row, list) and len(row) > 0 and isinstance(row[0], list):
                cleaned_reason.append(row[0])
            else:
                cleaned_reason.append(row)
        reason_matrix = cleaned_reason

    G = nx.DiGraph()

    # Add nodes
    for name in tool_names:
        G.add_node(name)

    if not adjacency_matrix:
        print(f"[WARN] {path}: empty adjacency_matrix")
        return G

    total_edges = 0

    # Now adjacency_matrix[i][j] is a plain bool
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

            reason = ""
            if reason_matrix is not None and i < len(reason_matrix):
                r_row = reason_matrix[i]
                if r_row is not None and j < len(r_row):
                    reason = r_row[j] or ""

            G.add_edge(tool_names[i], tool_names[j], reason=reason)
            total_edges += 1

    return G


def visualize_graph(G: nx.DiGraph, title: str, out_html: str) -> None:
    net = Network(height="800px", width="100%", directed=True, notebook=True)
    net.barnes_hut()

    # Nodes
    for node in G.nodes:
        net.add_node(node, label=node)

    # Edges with label + hover tooltip
    for source, target, data in G.edges(data=True):
        reason = (data.get("reason") or "").strip()
        short = (reason[:40] + "…") if len(reason) > 40 else reason

        net.add_edge(
            source,
            target,
            arrows="to",
            label=short if short else None,   # visible on the edge
            title=reason if reason else None, # full tooltip on hover
        )

    net.title = title
    net.show(out_html)


def main():
    json_paths = sorted(
        glob.glob(os.path.join(OUTPUT_DIR, "**", PATTERN), recursive=True)
    )

    if not json_paths:
        print(f"No JSON files found in {OUTPUT_DIR}")
        return

    for path in json_paths:
        basename = os.path.splitext(path)[0]
        html_name = f"{basename}_graph.html"
        print(f"Processing {path} -> {html_name}")

        try:
            G = build_graph_from_json(path)
            visualize_graph(G, title=basename, out_html=html_name)
        except Exception as e:
            print(f"Failed to process {path}: {e}")


if __name__ == "__main__":
    main()