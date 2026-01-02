import json
import random
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Literal, Optional

# from is_nested_model import build_chain as nested_model_chain


@dataclass
class Tool:
    idx: int
    name: str
    info: Dict[str, Any]
    neighbors: List[int] = field(default_factory=list)
    neighbor_reasons: Dict[int, str] = field(default_factory=dict)

Turn = List[Tool]           # one or more tools in a single "turn"
TRACE = List[Turn]          # sequence of turns

def load_graph_tools(json_path: str):
    """
    Load the tool graph from the JSON file produced by neighbour_app.py.

    This populates each Tool with:
      - neighbors: list of neighbor tool indices
      - neighbor_reasons: mapping neighbor index -> textual reason for the edge
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    tools_raw = data["tools"]
    adjacency_matrix = data["adjacency_matrix"]
    reason_matrix = data.get("reason_matrix", None)

    for i in range(len(adjacency_matrix)):
        if len(adjacency_matrix[i]) != len(tools_raw):
            raise ValueError(f"Adjacency matrix row {i} length mismatch: expected {len(tools_raw)}, got {len(adjacency_matrix[i])}")
    for i in range(len(reason_matrix)):
        if len(reason_matrix[i]) != len(tools_raw):
            raise ValueError(f"Reason matrix row {i} length mismatch: expected {len(tools_raw)}, got {len(reason_matrix[i])}")

    tools: List[Tool] = [
        Tool(idx=i, name=t["name"], info=t["info"])
        for i, t in enumerate(tools_raw)
    ]

    # Populate neighbor information directly on each Tool instance
    if adjacency_matrix is not None:
        for i, row in enumerate(adjacency_matrix):
            for j, is_neigh in enumerate(row):
                if not is_neigh:
                    continue
                tools[i].neighbors.append(j)
                if reason_matrix is not None:
                    # reason_matrix is expected to be aligned with adjacency_matrix
                    tools[i].neighbor_reasons[j] = reason_matrix[i][j]
    return tools

def random_walk(
    tools: List[Tool],
    steps: int = 7,
    start_tool: Optional[Tool] = None,
    rng: random.Random = None,
) -> TRACE:
    """
    Simple random walk on neighbour graph starting from a given tool.

    - Uses Tool.neighbors (indices) to move.
    - Avoids loops: once a tool would be revisited, the walk stops.

    Returns an TRACE with shape: [[tool1], [tool2], ..., [toolH]].
    """
    if rng is None:
        rng = random

    if start_tool is None:
        # choose any node as start; you can plug in your "SearchUser" entry if needed
        current_idx = rng.randint(0, len(tools) - 1)
    else:
        current_idx = start_tool.idx

    visited: set[int] = set()
    visited.add(current_idx)

    trace: TRACE = [[tools[current_idx]]]

    for _ in range(steps - 1):
        nbrs = tools[current_idx].neighbors
        if not nbrs:
            # dead end; stop the walk
            break

        # filter out already visited neighbors to avoid loops
        candidates = [j for j in nbrs if j not in visited]
        if not candidates:
            # all neighbors already visited -> adding any would create a loop
            break

        next_idx = rng.choice(candidates)

        current_idx = next_idx
        visited.add(current_idx)
        trace.append([tools[current_idx]])
    return trace

def build_random_walks(
    tools: List[Tool],
    num_walks: int,
    walk_steps: List[int] = [1, 3, 5],
    rng: Optional[random.Random] = None,
) -> List[TRACE]:
    """
    Build multiple random-walk TRACEs on the tool graph.
    """
    if rng is None:
        rng = random.Random(42)

    traces: List[TRACE] = []
    for _ in range(num_walks):
        trace = random_walk(tools, steps=rng.choice(walk_steps), start_tool=rng.choice(tools), rng=rng)
        traces.append(trace)

    return traces