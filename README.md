# Magnet-TAU

Generate tool graphs, sample traces, and produce downstream tasks.

## 1. Environment Setup [TODO]

Python `3.10` is the target version.

### Conda

```bash
conda create -n tracer python=3.10 -y
conda activate tracer
pip install -r requirements.txt
```

### venv

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Create `.env` [TODO]

Create `.env` in the repo root before running any script.

```bash
OPENAI_API_KEY=your_openai_api_key
HOSTED_VLLM_API_KEY=your_hosted_vllm_api_key
VLLM_API_KEY=your_vllm_api_key
```

- `OPENAI_API_KEY` for OpenAI models
- `HOSTED_VLLM_API_KEY` for hosted models
- `VLLM_API_KEY` for hosted models

If a hosted model is used, set both `HOSTED_VLLM_API_KEY` and `VLLM_API_KEY`.

## 3. Build Graphs using `graph_builder.py` [DONE]

This step is already done. Re-run only if you want to rebuild graph JSONs.

```bash
python graph_builder.py \
  --provider openai \
  --model gpt-5.2 \
  --temperature 0.0 \
  --domains airline retail telecom telehealth
```

Recommended graph JSON files:

| Domain | Graph JSON |
| --- | --- |
| `airline` | `output/graphs/openai_gpt-5.2/airline_adjacency_matrix_0.0.json` |
| `retail` | `output/graphs/openai_gpt-5.2/retail_adjacency_matrix_0.0.json` |
| `telecom` | `output/graphs/openai_gpt-5.2/telecom_adjacency_matrix_0.0.json` |
| `telehealth` | `output/graphs/openai_gpt-5.2/telehealth_adjacency_matrix_0.0.json` |

## 4.1 Sampling Traces using `build_trace_v2.py` [TODO]

Run once per graph JSON to generate traces for task generation.

TODO before running:

- set `--graph_json_path` to the target domain graph
- adjust `--num-traces` if you want more or fewer traces

```bash
python build_trace_v2.py \
  --graph_json_path output/graphs/openai_gpt-5.2/airline_adjacency_matrix_0.0.json \
  --num-traces 50 \
  --walk-steps 2 3 4 \
  --extra-turn-prob 0.3 \
  --random-seed 10
```

Output:

```text
output/traces/<graph_name>_traces.json
```

## 4.2 Generating Tasks using `generator.py` [TODO]

Update `tracer2/config/generator_config.json`, then run:

TODO before running:

- set `env` to the target domain
- set `trace_path` to the matching traces file
- set `generator_model_provider`, `generator_model`, and `api_base` for the model you want to use
- optionally use `task_ids`, `start_index`, and `end_index` to control which tasks are generated

```bash
python -m tracer2.generator --config tracer2/config/generator_config.json
```

Key config fields:

- `env`
- `trace_path`
- `generator_model_provider`
- `generator_model`
- `api_base`
- `start_index`
- `end_index`
- `task_ids`

## 5. Generate Emotion Bank [DONE]

Use `emotions/build_emotion_instruction_graph.py`.

```bash
python emotions/build_emotion_instruction_graph.py \
  --config emotions/emotion_instruction_graph_config.json
```

Output:

```text
emotions/emotion_instructions.generated.json
```

Key config options in `emotions/emotion_instruction_graph_config.json`:

- `model`, `provider`, `base_api`: model backend settings
- `max_blends`: increases the number of emotion blends per category
- `instructions_per_blend`: increases the number of instruction variants per blend
- `recursion_limit`: increase if the workflow needs more graph steps for larger runs
- `emotion_bank_path`: input emotion bank JSON
- `output_path`: generated instruction JSON
- `graph_png_path`: workflow graph PNG

## 6. Extend Telehealth Data [TODO]

Use `data_extender/telehealth/extend_telehealth.py`.

TODO before running:

- set `input_data_dir`, for example `tau_bench/envs/telehealth/data/`
- set `target_new_patients`, `target_family_groups`, `target_new_providers`, `target_new_devices`, and `target_scenarios`
- adjust `scenario_mix` for the scenario distribution you want
- set `model` and `provider`

```bash
python data_extender/telehealth/extend_telehealth.py \
  --config data_extender/telehealth/extend_telehealth_config.json
```

Key config options in `data_extender/telehealth/extend_telehealth_config.json`:

- `input_data_dir`: source telehealth dataset, for example `tau_bench/envs/telehealth/data/`
- `target_new_patients`, `target_family_groups`, `target_new_providers`, `target_new_devices`: deterministic master-data growth
- `target_scenarios`: number of scenario blueprints and generated scenario cases
- `scenario_mix`: distribution across scenario types
- `model`, `provider`: model generation settings

To increase generations:

- increase `target_scenarios` to generate more scenario cases
- increase `target_new_patients`, `target_new_providers`, and `target_new_devices` to expand the underlying dataset
- adjust `scenario_mix` if you want more of specific scenario types
