#!/usr/bin/env python3
"""
visualize_trace.py

Reads a traces JSON (list of traces -> list of turns -> list of tool dicts)
and writes one Mermaid graph per trace, so you can inspect each sampled path
individually without merging counts across traces.

Usage:
    python visualize_trace.py traces.json -o out_dir -p airline_trace

This will write:
    out_dir/airline_trace_trace_000.mmd
    out_dir/airline_trace_trace_001.mmd
    ...

Each .mmd contains a fenced Mermaid 'graph TD' block which you can open in
VSCode Markdown preview or paste into the Mermaid Live Editor.

Notes:
- The script assumes each turn is a list and usually contains a single tool dict.
- neighbor_reasons keys in traces are handled as strings or ints.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple


def sanitize_label(s: str | None, max_len: int = 240) -> str:
    """Prepare text for Mermaid edge label: remove newlines, collapse whitespace,
    and truncate to max_len chars (keeps it readable)."""
    if s is None:
        return ""
    s = re.sub(r"\s+", " ", str(s)).strip()
    if len(s) > max_len:
        s = s[: max_len - 3] + "..."
    s = s.replace("|", "/")
    s = s.replace('"', "'")
    return s


def build_nodes_and_edges_for_trace(trace: List[List[Dict[str, Any]]]):
    """
    From a single trace (list of turns), where each turn is a list of tool dicts,
    produce:
      - nodes: dict[idx] = name  (tool idx assumed globally unique)
      - edges: list of (src_idx, dst_idx, reason)

    Visualization semantics:
      - Tools inside the same turn are shown in the given order and connected
        sequentially (tool1 -> tool2 -> ...).
      - The last tool of a turn connects to the first tool of the next turn
        (end-of-turn -> start-of-next-turn), preserving inter-turn ordering.

    This keeps turn grouping visible while producing a single linear execution
    order suitable for Mermaid rendering.
    """
    nodes: Dict[int, str] = {}
    edges: List[Tuple[int, int, str]] = []

    # Map tool idx -> tool dict for neighbor_reasons lookup
    tool_map: Dict[int, Dict[str, Any]] = {}

    # Each element of turns_indices is a list of tool idxs for that turn
    turns_indices: List[List[int]] = []

    for turn in trace:
        if not turn:
            continue
        turn_idxs: List[int] = []
        for tool in turn:
            idx = int(tool["idx"])
            nodes[idx] = tool.get("name", f"tool_{idx}")
            tool_map[idx] = tool
            turn_idxs.append(idx)
        if turn_idxs:
            turns_indices.append(turn_idxs)

    # Build edges inside each turn (sequential tools)
    for turn_idxs in turns_indices:
        for a_idx, b_idx in zip(turn_idxs, turn_idxs[1:]):
            nr = tool_map.get(a_idx, {}).get("neighbor_reasons") or {}
            reason = nr.get(str(b_idx)) or nr.get(b_idx) or ""
            reason = sanitize_label(reason)
            edges.append((a_idx, b_idx, reason))

    # Link end of each turn to start of next turn
    for t in range(len(turns_indices) - 1):
        src = turns_indices[t][-1]
        dst = turns_indices[t + 1][0]
        nr = tool_map.get(src, {}).get("neighbor_reasons") or {}
        reason = nr.get(str(dst)) or nr.get(dst) or ""
        reason = sanitize_label(reason)
        edges.append((src, dst, reason))

    return nodes, edges


def write_mermaid_for_trace(
    nodes: Dict[int, str], edges: List[Tuple[int, int, str]], out_path: Path, title: str | None = None
):
    """
    Write a Mermaid 'graph TD' for a single trace.
    """
    p = out_path
    p.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    lines.append("```mermaid")
    lines.append("graph TD")
    if title:
        lines.append(f"%% {title}")

    # Add nodes
    for idx, name in sorted(nodes.items()):
        node_id = f"t{idx}"
        label = name.replace('"', "'")
        lines.append(f'{node_id}["{label}"]')

    # Add edges with reason label
    for src, dst, reason in edges:
        node_src = f"t{src}"
        node_dst = f"t{dst}"
        label = f"{reason}" if reason else ""
        label = label.replace("|", "/").replace('"', "'")
        if label:
            lines.append(f'{node_src} -->|"{label}"| {node_dst}')
        else:
            lines.append(f'{node_src} --> {node_dst}')

    lines.append("```")
    p.write_text("\n".join(lines), encoding="utf-8")
    print(f"[INFO] Wrote {p.resolve()}")


def main():
    parser = argparse.ArgumentParser(description="Write one Mermaid file per trace")
    parser.add_argument("traces_json", help="Path to traces JSON (list of traces)")
    parser.add_argument(
        "-o",
        "--out-dir",
        default=None,
        help="Output directory (defaults to a folder next to the JSON, named after the file)",
    )
    parser.add_argument("-p", "--out-prefix", default="trace", help="Output file prefix")
    parser.add_argument("--merged", action="store_true", help="Also write a merged graph combining all traces")
    args = parser.parse_args()

    traces_path = Path(args.traces_json)
    if not traces_path.exists():
        raise FileNotFoundError(traces_path)

    # Determine output directory: if not provided, place next to JSON and name after JSON stem
    if args.out_dir is None:
        out_dir = traces_path.parent / traces_path.stem
    else:
        out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(traces_path.read_text(encoding="utf-8"))

    # Write one file per trace
    for i, trace in enumerate(data):
        nodes, edges = build_nodes_and_edges_for_trace(trace)
        out_file = out_dir / f"{args.out_prefix}_trace_{i:03d}.md"
        title = f"Trace {i}"
        write_mermaid_for_trace(nodes, edges, out_file, title=title)

    # Optionally write merged graph
    if args.merged:
        # Aggregate nodes and edge counts + reasons across traces
        agg_nodes: Dict[int, str] = {}
        agg_edges: Dict[Tuple[int, int], Dict[str, Any]] = defaultdict(lambda: {"count": 0, "reasons": []})
        for trace in data:
            nodes, edges = build_nodes_and_edges_for_trace(trace)
            for idx, name in nodes.items():
                agg_nodes[idx] = name
            for src, dst, reason in edges:
                key = (src, dst)
                agg_edges[key]["count"] += 1
                if reason and reason not in agg_edges[key]["reasons"]:
                    agg_edges[key]["reasons"].append(reason)

        # Emit merged mermaid
        merged_lines: List[str] = []
        merged_lines.append("```mermaid")
        merged_lines.append("graph TD")
        merged_lines.append(f"%% Merged graph ({len(data)} traces)")
        for idx, name in sorted(agg_nodes.items()):
            node_id = f"t{idx}"
            label = name.replace('"', "'")
            merged_lines.append(f'{node_id}["{label}"]')

        for (src, dst), meta in agg_edges.items():
            node_src = f"t{src}"
            node_dst = f"t{dst}"
            reasons = " / ".join(meta["reasons"]) if meta["reasons"] else ""
            label = f"{reasons} ({meta['count']})" if reasons else f"({meta['count']})"
            label = label.replace("|", "/").replace('"', "'")
            merged_lines.append(f'{node_src} -->|"{label}"| {node_dst}')

        merged_lines.append("```")
        merged_out = out_dir / f"{args.out_prefix}_merged.mmd"
        merged_out.write_text("\n".join(merged_lines), encoding="utf-8")
        print(f"[INFO] Wrote merged graph to {merged_out.resolve()}")


if __name__ == "__main__":
    main()