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

## Pipeline sketch

```text
graph_builder.py       → output/graphs/...
extend_telehealth.py   → extended telehealth JSON (optional)
build_trace_v3.py      → output/traces/...
tracer2/generator.py   → output/tasks/...
emotions/              → emotions/output/emotion_persona_instructions.json
emotion_analysis/      → encode instructions, train encoder+kNN, attach predictions to tasks, analysis/ plots
```

For more architecture notes (agents, envs, trace semantics), see **[CLAUDE.md](CLAUDE.md)**.
