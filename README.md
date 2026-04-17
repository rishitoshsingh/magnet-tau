# Magnet-TAU

Synthetic task generation for multi-domain customer service agents: tool graphs, traces, generated tasks, and optional emotion enrichment.

Supported domains: **airline**, **retail**, **telecom**, **telehealth**.

---

## 1. Environment setup

Python **3.10** is the target version.

### Conda

```bash
conda create -n magnet-tau python=3.10 -y
conda activate magnet-tau
pip install -r requirements.txt
```

### venv

```bash
python3.10 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## 2. Create `.env`

Create a `.env` file in the **repository root** before running scripts that call LLM or embedding APIs.

```bash
OPENAI_API_KEY=...
HOSTED_VLLM_API_KEY=...   # hosted models
VLLM_API_KEY=...          # hosted models
```

- **OpenAI**: graph building, trace/task generation, embeddings, emotion batch jobs, etc.
- **Hosted VLLM**: set both `HOSTED_VLLM_API_KEY` and `VLLM_API_KEY` when using that stack.
- **LangSmith**: optional tracing for LangChain/LangGraph pipelines.

---

## 3. Extend telehealth data (optional)

Deterministic growth of telehealth JSON data and scenario blueprints. Configure paths and targets in the config file, then run:

```bash
python data_extender/telehealth/extend_telehealth.py \
  --config data_extender/telehealth/extend_telehealth_config.json
```

Key ideas: `input_data_dir`, `target_new_patients` / providers / devices, `target_scenarios`, `scenario_mix`, and model settings in that JSON.

---

## 4. Graph construction

Build tool adjacency graphs (nodes = tools, edges = valid call sequences). Re-run only when you need to rebuild graphs.

```bash
python graph_builder.py \
  --provider openai \
  --model gpt-5.2 \
  --temperature 0.0 \
  --domains airline retail telecom telehealth
```

Example outputs:

| Domain | Graph JSON (example path) |
| --- | --- |
| airline | `output/graphs/openai_gpt-5.2/airline_adjacency_matrix_0.0.json` |
| retail | `output/graphs/openai_gpt-5.2/retail_adjacency_matrix_0.0.json` |
| telecom | `output/graphs/openai_gpt-5.2/telecom_adjacency_matrix_0.0.json` |
| telehealth | `output/graphs/openai_gpt-5.2/telehealth_adjacency_matrix_0.0.json` |

---

## 5. Trace sampling

Sample traces from a graph JSON with deterministic distributions (`walk_steps` / `num_intents` and their weights). Always pass `--random-seed` for reproducibility.

```bash
python build_trace_v3.py \
  --graph_json_path output/graphs/openai_gpt-5.2/airline_adjacency_matrix_0.0.json \
  --num-traces 1000 \
  --walk-steps 2 3 4 \
  --walk-steps-dist 0.5 0.3 0.2 \
  --num-intents 1 2 3 \
  --num-intents-dist 0.6 0.3 0.1 \
  --random-seed 10
```

- Set `--graph_json_path` to the domain graph you want.
- Distributions must sum to `1.0`.

Traces are written under `output/traces/` (filename derived from the graph stem).

---

## 6. Task generator

`tracer2/generator.py` turns traces into natural-language tasks (multi-agent LangGraph pipeline). Point a **per-domain** config at the matching traces file and model settings.

```bash
python -m tracer2.generator --config tracer2/config/generator_config_airline.json
```

Typical config fields: `env`, `trace_path`, `generator_model_provider`, `generator_model`, `api_base`, and optional `start_index` / `end_index` / `task_ids`.

Generated tasks are written under `output/tasks/` (exact path depends on your generator config).

---

## 7. Emotion persona instructions

Batch generation of emotion persona instructions (OpenAI Batch API), config, and outputs are documented here:

**[emotions/README.md](emotions/README.md)**

---

## 8. Emotion analysis

Encode emotion instructions, train the encoder + kNN, run inference on tasks, and produce analysis plots (`run_all.py`).

**This step is what adds emotion instruction / novel-emotion predictions onto your generated tasks** (e.g. sidecar or suffixed JSON with `novel_emotion_prediction` per task, as configured in `emotion_analysis/config.json`). Without running it, tracer output alone does not include that layer.

**[emotion_analysis/README.md](emotion_analysis/README.md)**

---

## 9. Generated tasks viewer

Local Flask UI to browse `*_generated_tasks.json` files (accordion layout, trajectories, action traces).

**[generated_tasks_viewer/README.md](generated_tasks_viewer/README.md)**

---

## 10. Export tasks to env `TASKS` files

To turn a generated JSON list (e.g. `output/tasks/*_generated_tasks*.json`) into a Python module the eval stack expects, use **`export_tasks.py`**. It writes a file that defines `TASKS = [ Task(...), ... ]` with `from tau_emotion_bench.types import Task, Action`, and skips rows that failed or lack a usable `user_id`. If `novel_emotion_prediction` is present, the exporter can fold the top matched emotion instruction into the task text and emit optional emotion dimension fields.

**1. Clone the emotion-bench checkout** (anywhere you like—sibling directory, separate workspace, etc.):

```bash
git clone https://github.com/rishitoshsingh/tau-emotion-bench.git /path/to/tau-emotion-bench
```

**2. Run the export from this repo**, pointing **`--package`** at that project’s import root and **`--output`** under **`tau_emotion_bench/env/<domain>/`** in the clone (e.g. **`tasks_dec.py`** for a dev-style split, or other `tasks_*.py` filenames you use).

```bash
python export_tasks.py output/tasks/airline_adjacency_matrix_0.0_generated_tasks.json \
  --package tau_emotion_bench \
  --output /path/to/tau-emotion-bench/tau_emotion_bench/env/airline/tasks_dev.py
```

- **`--package`**: must be **`tau_emotion_bench`** so imports match [tau-emotion-bench](https://github.com/rishitoshsingh/tau-emotion-bench).
- **`--output`**: absolute or relative path inside the clone at **`tau_emotion_bench/env/<domain>/tasks_dec.py`** (adjust `<domain>` and filename as needed).

If your tasks are not already split across JSON files, partition the list (or run the exporter per slice) so each export targets the right file under `tau_emotion_bench/env/<domain>/`.

---

## 11. Task evaluation

`evaluator/` is a quality-audit subproject that scores every generated task against four criteria and produces a pass/fail verdict plus a statistical summary.

### Criteria

| # | Criterion | Violation condition |
|---|---|---|
| 1 | **Goal-oriented** | Instruction is procedural — the agent would need to elicit information from the user before it can execute anything |
| 2 | **Template** | `preference_instruction` is missing either a concrete tool-calling task or a user preference |
| 3 | **Solvable by ground truth** | Ground-truth action sequence fails in the environment, or the `solvable` field is `false` |
| 4 | **No domain violation** | Task is out-of-domain but the ground truth attempts execution instead of calling the handoff tool (`transfer_to_human_agents` / `transfer_to_human_support`) |

Criteria 1 and 2 are evaluated on the **`preference_instruction`** field only (the post-processed rewrite). Criteria 3 and 4 use deterministic checks against existing fields first; an LLM fallback is invoked only when those are inconclusive.

### Step 1 — Evaluate tasks

```bash
python -m evaluator.runner --config evaluator/config/eval_config_airline.json
# or
python -m evaluator.runner \
  --input-path output/traces/airline_adjacency_matrix_0.0_generated_tasks.json \
  --domain airline \
  --eval-model gpt-4.1 --eval-model-provider openai
```

Output: `output/evaluations/<name>_eval.json` — one `TaskEvaluation` record per task with per-criterion verdicts, reasons, and an `overall_passed` flag.

Config fields: `input_path`, `domain`, `eval_model_provider`, `eval_model`, `api_base`, `start_index` / `end_index` / `task_ids`.

Per-domain configs are in `evaluator/config/`.

### Step 2 — Orchestrate / summarise

```bash
python -m evaluator.orchestrator \
  --eval-path output/evaluations/airline_adjacency_matrix_0.0_eval.json \
  --domain airline \
  --eval-model gpt-4.1 --eval-model-provider openai \
  --markdown-out report.md
```

Output: `*_summary.json` (and optional Markdown) containing:
- **`good_tasks`** / **`bad_tasks`** — clear per-task verdict list
- **`per_criterion`** — violation counts and rates for each of the four criteria
- **`co_occurrence`** — how often multiple criteria fail together
- **`error_categories`** — LLM-grouped themes explaining *why* tasks fail (e.g. "Insufficient gift card balance", "Missing user preference")
- **`llm_summary`** — 3–5 sentence executive insight + actionable recommendation

Omit `--eval-model` to run in programmatic-only mode (no LLM calls, instant).

---

## Pipeline sketch

```text
graph_builder.py          → output/graphs/...
extend_telehealth.py      → extended telehealth JSON (optional)
build_trace_v3.py         → output/traces/...
tracer2/generator.py      → output/tasks/...
evaluator/runner.py       → output/evaluations/..._eval.json      (4-criteria quality audit)
evaluator/orchestrator.py → output/evaluations/..._summary.json   (good/bad verdict + stats)
emotions/                 → emotions/output/emotion_persona_instructions.json
emotion_analysis/         → encode instructions, train encoder+kNN, attach predictions to tasks, analysis/ plots
export_tasks.py           → <tau-emotion-bench>/tau_emotion_bench/env/<domain>/tasks_dec.py
```

For more architecture notes (agents, envs, trace semantics), see **[CLAUDE.md](CLAUDE.md)**.
