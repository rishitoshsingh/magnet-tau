from dotenv import load_dotenv

load_dotenv()
from tracer.task_generator import TracerAgent
from tracer.types import RunConfig


def main():
    config = RunConfig(
        env="airline",                     # or "retail"
        trace_path="output/traces/airline_adjacency_matrix_0.0_traces.json",  # path to traces
        model_provider="openai",
        model="gpt-5.2",              # or whatever you use
        temperature=0.2,
        task_ids=None,                     # run a slice
        start_index=0,
        end_index=10,
    )

    agent = TracerAgent(config)

    for task_id, result in agent.run():
        print(f"\n✅ Generated task {task_id}")
        print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    main()