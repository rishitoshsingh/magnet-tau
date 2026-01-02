
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

Run `run_task_generator.py` using the traces produced in step 1.

```bash
python run_task_generator.py \
  --env airline \
  --trace-path output/traces/<graph_name>_traces.json \
  --model-provider openai \
  --model gpt-5.2 \
  --temperature 0.2 \
  --start-index 0 \
  --end-index 10
```

**Arguments**

- `--env`: Environment (`airline` or `retail`)
- `--trace-path`: Path to the traces JSON file
- `--model-provider`: LLM provider (default: `openai`)
- `--model`: Model name
- `--temperature`: Sampling temperature
- `--task-ids`: Optional list of specific task IDs to run
- `--start-index`: Start index for trace slicing
- `--end-index`: End index for trace slicing (omit to run all)

---

## Example (end-to-end)

```bash
python build_trace_v2.py \
  --graph_json_path graphs/airline_adjacency_matrix_0.0.json

python run_task_generator.py \
  --env airline \
  --trace-path output/traces/airline_adjacency_matrix_0.0_traces.json
```

---

## Notes

- Environment variables (e.g., API keys) are loaded via `.env`
- If no CLI arguments are provided, scripts fall back to sensible defaults
