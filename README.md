
# Magnet-TAU

This project generates tool-use traces from a graph and then uses those traces to generate downstream tasks.

## Environment Setup

This project is tested with **Python 3.10**. Please create and activate a Python 3.10 environment before installing dependencies.

### Using conda

```bash
conda create -n tracer python=3.10 -y
conda activate tracer
pip install -r requirements.txt
```

### Using venv

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Create `.env`

Before running any script, create a `.env` file in the project root and add the required API keys.

```bash
OPENAI_API_KEY=your_openai_api_key
HOSTED_VLLM_API_KEY=your_hosted_vllm_api_key
VLLM_API_KEY=your_vllm_api_key
```

- `OPENAI_API_KEY`: Required when using OpenAI models
- `HOSTED_VLLM_API_KEY`: Required when using a hosted model
- `VLLM_API_KEY`: Required when using a hosted model

If you are using a hosted model, make sure both `HOSTED_VLLM_API_KEY` and `VLLM_API_KEY` are set before running the generator or any other script that depends on model access.

## Usage

The workflow consists of **two steps**:

---

## 1️⃣ Build traces from a tool graph

Run `build_trace_v2.py` to generate random-walk traces from a graph JSON.

```bash
python build_trace_v2.py \
  --graph_json_path path/to/your_graph.json \
  --num-traces 50 \
  --walk-steps 2 3 4
```

**Arguments**

- `--graph_json_path` (required): Path to the graph JSON file
- `--num-traces`: Number of traces to generate (default: `50`)
- `--walk-steps`: List of walk step sizes per turn (default: `2 3 4`)

This will write a traces file to:

```
output/traces/<graph_name>_traces.json
```

---

## 2️⃣ Generate tasks from traces

Before running the generator, update `tracer2/config/generator_config.json` with the correct environment, trace path, model settings, and any index range you want to use.

```bash
python -m tracer2.generator --config tracer2/config/generator_config.json
```

**Config fields**

- `--env`: Environment (`airline` or `retail`)
- `trace_path`: Path to the traces JSON file
- `generator_model_provider`: LLM provider (default: `openai`)
- `generator_model`: Model name
- `task_ids`: Optional list of specific task IDs to run
- `start_index`: Start index for trace slicing
- `end_index`: End index for trace slicing

---

## Example (end-to-end)

```bash
python build_trace_v2.py \
  --graph_json_path graphs/airline_adjacency_matrix_0.0.json

# First update tracer2/config/generator_config.json
python -m tracer2.generator --config tracer2/config/generator_config.json
```

---

## Notes

- Environment variables (e.g., API keys) are loaded via `.env`
- If no CLI arguments are provided, scripts fall back to sensible defaults
