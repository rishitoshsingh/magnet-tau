import json
import os
import random
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Literal, Optional

import langchain_core
from is_nested_model import build_chain as nested_model_chain
from tqdm import tqdm


# -----------------------------
# Data structures
# -----------------------------
@dataclass
class Tool:
    idx: int
    name: str
    info: Dict[str, Any]  # whatever tau-bench put in get_info()


Turn = List[Tool]           # one or more tools in a single turn
FSP = List[Turn]            # full function sequence plan


# -----------------------------
# Load graph from adjacency JSON
# -----------------------------
def load_graph(json_path: str):
    """
    Load tools + adjacency_matrix + reason_matrix from the JSON file produced
    by neighbour_app.py.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    tools_raw = data["tools"]
    adjacency_matrix = data["adjacency_matrix"]  # list[list[bool]]
    reason_matrix = data.get("reason_matrix", None)

    tools: List[Tool] = [
        Tool(idx=i, name=t["name"], info=t["info"])
        for i, t in enumerate(tools_raw)
    ]

    # neighbors[i] = list of indices j where adjacency_matrix[i][j] is True
    neighbors: Dict[int, List[int]] = {}
    for i, row in enumerate(adjacency_matrix):
        neighbors[i] = [j for j, is_neigh in enumerate(row) if is_neigh]

    return tools, neighbors, reason_matrix


# -----------------------------
# 2. Random walk FSP sampling
# -----------------------------
def random_walk_fsp(
    tools: List[Tool],
    neighbors: Dict[int, List[int]],
    steps: int = 7,
    start_indices: Optional[List[int]] = None,
    rng: Optional[random.Random] = None,
) -> FSP:
    """
    Simple random walk on neighbour graph.
    Returns FSP with shape: [[tool1], [tool2], ..., [toolH]].
    """
    if rng is None:
        rng = random

    if start_indices is None:
        # choose any node as start; you can plug in your "SearchUser" entry if needed
        start_idx = rng.randint(0, len(tools) - 1)
    else:
        start_idx = rng.choice(start_indices)

    current = start_idx
    fsp: FSP = [[tools[current]]]

    for _ in range(steps - 1):
        nbrs = neighbors.get(current, [])
        if not nbrs:
            # dead end; you can either break or jump to a new random node
            break
        current = rng.choice(nbrs)
        fsp.append([tools[current]])

    return fsp


# -----------------------------
# 3. Node operations
# -----------------------------
# 3.1 MERGE: combine consecutive turns
def merge_fsp(
    fsp: FSP,
    p_merge: float = 0.3,
    rng: Optional[random.Random] = None,
) -> FSP:
    """
    With probability p_merge, merge turn i and i+1 into one turn (short dependency).
    """
    if rng is None:
        rng = random

    merged: FSP = []
    i = 0
    while i < len(fsp):
        if i < len(fsp) - 1 and rng.random() < p_merge:
            merged.append(fsp[i] + fsp[i + 1])
            i += 2
        else:
            merged.append(fsp[i])
            i += 1
    return merged


# 3.2 INSERT: nested + long dependency
# In Magnet they use an LLM to decide "nested"; here we expose a hook.
def default_is_nested(source: Tool, candidate: List[Tool]) -> bool:
    # chain = nested_model_chain("openai","gpt-5", 0.1, None)
    chain = nested_model_chain("deepseek","deepseek-reasoner", 0.1, None)
    result = chain.invoke({
        "function_f": json.dumps(asdict(source), ensure_ascii=False),
        "function_g": json.dumps([asdict(tool) for tool in candidate], ensure_ascii=False),})
    if isinstance(result, langchain_core.messages.ai.AIMessage):
        print("Raw model output:", result.content)
        data = json.loads(result.content)
        answer = data.get("answer", [False])
    else:
        answer = result.answer
    return answer

# def default_is_nested(source: Tool, candidate: Tool) -> bool:
#     # chain = nested_model_chain("gemini","gemini-2.5-flash", 0.1, None)
#     chain = nested_model_chain("deepseek","deepseek-reasoner", 0.1, None)
#     result = chain.invoke({
#         "functino_f": json.dumps(source, ensure_ascii=False),
#         "function_g": json.dumps(candidate, ensure_ascii=False),})
#     if isinstance(result, langchain_core.messages.ai.AIMessage):
#         print("Raw model output:", result.content)
#         data = json.loads(result.content)
#         answer = data.get("answer", False)
#     else:
#         answer = result.answer
#     return answer


# def insert_nested_and_long_dep(
#     fsp: FSP,
#     tools: List[Tool],
#     neighbors: Dict[int, List[int]],
#     is_nested_fn=default_is_nested,
#     p_long_dep: float = 0.5,
#     rng: Optional[random.Random] = None,
# ) -> FSP:
#     """
#     For each turn:
#       - Take the last tool in that turn
#       - Look at its neighbors
#       - If any neighbor is "nested" wrt this tool, add it into the same turn
#       - With probability p_long_dep, also reuse that tool as a later turn (long dependency)
#     """
#     if rng is None:
#         rng = random

#     new_fsp: FSP = [list(turn) for turn in fsp]  # shallow copy

#     for turn_idx, turn in tqdm(enumerate(new_fsp), total=len(new_fsp), desc="Inserting nested and long dependency"):
#         if not turn:
#             continue
#         src_tool = turn[-1]
#         nbr_indices = neighbors.get(src_tool.idx, [])
#         print("Finding nested candidates for tool:", src_tool.name)
#         print("Neighbor indices:", nbr_indices)
#         nested_candidates: List[Tool] = []
#         for j in nbr_indices:
#             cand_tool = tools[j]
#             if is_nested_fn(src_tool, cand_tool):
#                 nested_candidates.append(cand_tool)

#         if not nested_candidates:
#             continue

#         nested_tool = rng.choice(nested_candidates)

#         # nested call: same turn
#         turn.append(nested_tool)

#         # long dependency: sometimes re-use later
#         if rng.random() < p_long_dep:
#             later_idx = rng.randint(turn_idx + 1, len(new_fsp))
#             new_fsp.insert(later_idx, [nested_tool])

#     return new_fsp

def insert_nested_and_long_dep(
    fsp: FSP,
    tools: List[Tool],
    neighbors: Dict[int, List[int]],
    is_nested_fn=default_is_nested,
    p_long_dep: float = 0.5,
    rng: Optional[random.Random] = None,
) -> FSP:
    """
    For each turn:
      - Take the last tool in that turn
      - Look at its neighbors
      - If any neighbor is "nested" wrt this tool, add it into the same turn
      - With probability p_long_dep, also reuse that tool as a later turn (long dependency)
    """
    if rng is None:
        rng = random

    new_fsp: FSP = [list(turn) for turn in fsp]  # shallow copy

    for turn_idx, turn in tqdm(enumerate(new_fsp), total=len(new_fsp), desc="Inserting nested and long dependency"):
        if not turn:
            continue
        src_tool = turn[-1]
        nbr_indices = neighbors.get(src_tool.idx, [])
        print("Finding nested candidates for tool:", src_tool.name)
        print("Neighbor indices:", nbr_indices)
        nested_candidates: List[Tool] = []
        cand_tools = [tools[j] for j in nbr_indices]
        is_nested_tools: List[bool] = is_nested_fn(src_tool, cand_tools)
        nested_candidates = [tool for tool, is_nested in zip(cand_tools, is_nested_tools) if is_nested]

        if not nested_candidates:
            continue

        nested_tool = rng.choice(nested_candidates)

        # nested call: same turn
        turn.append(nested_tool)

        # long dependency: sometimes re-use later
        # if rng.random() < p_long_dep:
        #     later_idx = rng.randint(turn_idx + 1, len(new_fsp))
        #     new_fsp.insert(later_idx, [nested_tool])

    return new_fsp


# 3.3 SPLIT: introduce missing function / params marker
MissingKind = Literal["miss_params", "miss_func"]


@dataclass
class MissingMarker:
    kind: MissingKind
    note: str | None = None


def apply_split(
    fsp: FSP,
    miss_kind: MissingKind = "miss_params",
    rng: Optional[random.Random] = None,
):
    """
    Insert a 'missing' turn somewhere after a randomly chosen existing turn.
    Turn type becomes: List[Tool | MissingMarker]
    """
    if rng is None:
        rng = random

    if len(fsp) < 2:
        return fsp  # nothing to do

    h = rng.randint(0, len(fsp) - 2)
    insert_pos = rng.randint(h + 1, len(fsp))

    missing_turn = [MissingMarker(kind=miss_kind)]

    new_fsp = []
    for i, turn in enumerate(fsp):
        new_fsp.append(turn)
        if i == insert_pos - 1:
            new_fsp.append(missing_turn)

    return new_fsp


# -----------------------------
# 4. High-level pipeline
# -----------------------------
def sample_enhanced_fsps_for_graph(
    json_path: str,
    num_fsps: int = 10,
    walk_steps: int = 3,
    p_merge: float = 0.3,
    rng_seed: Optional[int] = None,
    start_tools: Optional[List[str]] = None,
):
    """
    Entry point:
    - Load graph from adjacency JSON
    - Sample `num_fsps` random FSPs
    - Apply merge -> insert -> split (miss_params + miss_func variants)
    Returns a list of dicts per FSP, ready to dump to JSON.
    """
    rng = random.Random(rng_seed)
    tools, neighbors, reason_matrix = load_graph(json_path)
    start_indices = None
    if start_tools is not None:
        start_indices = [t.idx for t in tools if t.name in start_tools]
        if not start_indices:
            raise ValueError(f"start_tool '{start_tools}' not found in tools.")

    fsps_out = []

    for _ in tqdm(range(num_fsps), desc="Sampling enhanced FSPs"):
        print("Sampling base FSP...")
        base = random_walk_fsp(tools, neighbors, steps=walk_steps, rng=rng, start_indices=start_indices)
        print("Merging FSP...")
        merged = merge_fsp(base, p_merge=p_merge, rng=rng)

        # Insert (currently no-op unless you implement is_nested_fn)
        print("Inserting nested and long dependency...")
        inserted = insert_nested_and_long_dep(
            merged,
            tools,
            neighbors,
            is_nested_fn=default_is_nested,
            rng=rng,
        )

        print("Applying splits...")
        with_miss_params = apply_split(inserted, miss_kind="miss_params", rng=rng)
        with_miss_func = apply_split(inserted, miss_kind="miss_func", rng=rng)

        print("Serializing FSPs...")
        fsps_out.append(
            {
                "base": serialize_fsp(base),
                "merged": serialize_fsp(merged),
                "inserted": serialize_fsp(inserted),
                "miss_params": serialize_fsp(with_miss_params),
                "miss_func": serialize_fsp(with_miss_func),
            }
        )

    return fsps_out


# -----------------------------
# 5. Serialization helpers
# -----------------------------
def serialize_turn(turn: List[Any]):
    """
    Convert Turn[List[Tool | MissingMarker]] into JSON-safe structure.
    """
    out = []
    for item in turn:
        if isinstance(item, Tool):
            out.append(
                {
                    "type": "tool",
                    "idx": item.idx,
                    "name": item.name,
                    "info": item.info,
                }
            )
        elif isinstance(item, MissingMarker):
            out.append(
                {
                    "type": "missing",
                    "kind": item.kind,
                    "note": item.note,
                }
            )
        else:
            raise TypeError(f"Unknown item in turn: {item}")
    return out


def serialize_fsp(fsp: List[List[Any]]):
    return [serialize_turn(turn) for turn in fsp]