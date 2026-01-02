import argparse

from dotenv import load_dotenv

load_dotenv()

from tracer.task_generator import TracerAgent
from tracer.types import RunConfig


def parse_args():
    parser = argparse.ArgumentParser(description="Run Tracer task generation")

    parser.add_argument("--env", default="airline", choices=["airline", "retail"],
                        help="Environment to run against")
    parser.add_argument("--trace-path", default="output/traces/airline_adjacency_matrix_0.0_traces.json",
                        help="Path to traces JSON file")
    parser.add_argument("--model-provider", default="openai",
                        help="Model provider (e.g., openai)")
    parser.add_argument("--model", default="gpt-5.2",
                        help="Model name")
    parser.add_argument("--temperature", type=float, default=0.2,
                        help="Sampling temperature")
    parser.add_argument("--task-ids", nargs="*", default=None,
                        help="Optional list of task IDs to run")
    parser.add_argument("--start-index", type=int, default=0,
                        help="Start index for task slice")
    parser.add_argument("--end-index", type=int, default=None,
                        help="End index for task slice")

    return parser.parse_args()


def main():
    args = parse_args()

    config = RunConfig(
        env=args.env,
        trace_path=args.trace_path,
        model_provider=args.model_provider,
        model=args.model,
        temperature=args.temperature,
        task_ids=args.task_ids,
        start_index=args.start_index,
        end_index=args.end_index,
    )

    agent = TracerAgent(config)

    for task_id, result in agent.run():
        print(f"\n✅ Generated task {task_id}")
        print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()