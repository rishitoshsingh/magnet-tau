# Generated tasks viewer

Flask viewer for `*_generated_tasks.json` files with a single-page accordion layout.

## Setup

From the project root (or from this folder):

```bash
pip install -r generated_tasks_viewer/requirements.txt
```

## Run

Option 1: path from CLI

```bash
cd generated_tasks_viewer
python3 app.py ../output/traces/airline_adjacency_matrix_0.0_generated_tasks.json
```

Or from project root:

```bash
python3 generated_tasks_viewer/app.py output/traces/airline_adjacency_matrix_0.0_generated_tasks.json
```

Then open `http://127.0.0.1:5000/`.

Option 2: path from browser

```bash
cd generated_tasks_viewer
python3 app.py
```

Open `http://127.0.0.1:5000/`, enter a path, and click `Load`. Paths are relative to the project root.

You can also use a query param such as:

```text
http://127.0.0.1:5000/?path=output/traces/airline_adjacency_matrix_0.0_generated_tasks.json
```

## Usage

- Tasks are collapsed initially.
- Expanding a task shows `user_id`, `instruction`, `preference_instruction` or `preference_instructions`, `story`, `ground_truth_actions`, `action_trace`, and other metadata.
- `Trajectories` stays collapsed until clicked, then each trajectory expands into per-message conversation cards.
- `Action trace` is nested by turn and node so you can inspect the graph incrementally.
