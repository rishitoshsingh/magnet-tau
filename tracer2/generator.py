import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Allow running as a script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

load_dotenv()

import litellm

litellm.drop_params = True

from tracer2.agents.task_generator_agent import TraceTaskGeneratorAgent


def _default_output_path(trace_path: str) -> str:
    p = Path(trace_path)
    name = p.name
    if "traces" in name:
        name = name.replace("traces", "generated_tasks")
    else:
        name = name + ".generated_tasks.json"
    return str(p.with_name(name))


def _format_persona_description(persona: Dict[str, Any]) -> str:
    """Format persona into natural language description."""
    emotional_state = persona.get("emotional_state", "calm")
    urgency = persona.get("urgency", "medium")
    communication_style = persona.get("communication_style", "cooperative")
    
    persona_text = f"You are feeling {emotional_state}"
    
    if urgency == "high":
        persona_text += " and this matter is very urgent"
    elif urgency == "medium":
        persona_text += " and this matter is moderately urgent"
    else:
        persona_text += " and this is not particularly urgent"
    
    persona_text += ". "
    
    style_descriptions = {
        "brief": "Keep your responses concise and to the point",
        "detailed": "Provide detailed explanations and background information",
        "persistent": "Be persistent in getting your needs met and follow up on unresolved issues",
        "cooperative": "Be cooperative and work together to find solutions",
        "demanding": "Be firm and assertive about your requirements",
    }
    
    persona_text += style_descriptions.get(communication_style, "Communicate clearly")
    persona_text += "."
    
    return persona_text


def _create_combined_instruction(raw_instructions: List[str], persona: Dict[str, Any], story: str) -> str:
    """Combine raw instructions with persona to create a natural language instruction."""
    
    persona_desc = _format_persona_description(persona)
    
    # Start with story context if available
    combined = ""
    if story:
        combined = f"Context: {story}\n\n"
    
    # Add persona
    combined += f"{persona_desc}\n\n"
    
    # Add the main instruction flow
    if len(raw_instructions) == 1:
        combined += f"Your goal: {raw_instructions[0]}"
    else:
        combined += "Your goals (in order):\n"
        for i, inst in enumerate(raw_instructions, 1):
            combined += f"{i}. {inst}\n"
    
    return combined.strip()


def parse_args():
    p = argparse.ArgumentParser(
        description="Generate tasks from traces (generator only, no verification)."
    )
    p.add_argument(
        "--env",
        default="airline",
        choices=["airline"],
        help="Domain env (airline only for now).",
    )
    p.add_argument(
        "--trace-path",
        default="output/traces/airline_adjacency_matrix_0.0_traces.json",
        help="Path to traces JSON file.",
    )
    p.add_argument("--output-path", default=None, help="Where to write generated tasks JSON.")

    p.add_argument("--generator-model-provider", default="openai")
    p.add_argument("--generator-model", default="gpt-5.2")
    p.add_argument("--generator-temperature", type=float, default=0.2)

    p.add_argument("--start-index", "--start-idx", type=int, default=0)
    p.add_argument("--end-index", "--end-idx", type=int, default=None)
    p.add_argument("--task-ids", nargs="*", default=None)

    return p.parse_args()


def main():
    args = parse_args()
    with open(args.trace_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    # Support both `*_traces.json` (list of traces) and `*_tasks.json` (list of dicts with action_trace).
    if (
        isinstance(loaded, list)
        and len(loaded) > 0
        and isinstance(loaded[0], dict)
        and "action_trace" in loaded[0]
    ):
        traces = [item.get("action_trace") for item in loaded]
    else:
        traces = loaded

    output_path = args.output_path or _default_output_path(args.trace_path)
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    if args.env != "airline":
        raise ValueError("Only airline is supported by this script right now.")

    # Generator uses airline reverse tools + airline dataset
    from tracer2.envs.airline.data import load_data
    from tracer2.envs.airline.reverse_tools import ALL_TOOLS as REVERSE_TOOLS

    generator = TraceTaskGeneratorAgent(
        tools=REVERSE_TOOLS,
        data_load_func=load_data,
        model=args.generator_model,
        provider=args.generator_model_provider,
        temperature=args.generator_temperature,
    )

    if args.task_ids is not None and len(args.task_ids) > 0:
        idxs = [int(x) for x in args.task_ids]
    else:
        end = args.end_index if args.end_index is not None else len(traces)
        idxs = list(range(args.start_index, min(end, len(traces))))

    results: List[Dict[str, Any]] = []
    for idx in idxs:
        trace = traces[idx]

        print(f"\nGenerating task for trace idx={idx}...")
        
        try:
            (
                candidate,
                generator_messages,
                generator_tool_actions,
                generator_tool_history,
            ) = generator.generate(trace=trace, attempt=0, verifier_feedback=None)

            print(f"Generated task for idx={idx}:")
            print(f"  User ID: {candidate.user_id}")
            print(f"  Story: {candidate.story}")
            print(f"  Num raw instructions: {len(candidate.instructions)}")

            # Create the combined instruction
            persona_dict = candidate.persona.model_dump()
            combined_instruction = _create_combined_instruction(
                raw_instructions=candidate.instructions,
                persona=persona_dict,
                story=candidate.story
            )

            results.append(
                {
                    "task_id": idx,
                    "user_id": candidate.user_id,
                    "raw_instructions": candidate.instructions,  # Original list of instructions
                    "instruction": combined_instruction,  # New combined natural language instruction
                    "story": candidate.story,
                    "persona": persona_dict,
                    "action_trace": candidate.action_trace,
                    "generator_traj": generator_messages,
                    "generator_tool_actions": generator_tool_actions,
                    "generator_tool_history": generator_tool_history,
                }
            )
            print(f"✓ Successfully generated task idx={idx}")
            
        except Exception as e:
            print(f"✗ Failed to generate task idx={idx}: {e}")
            results.append(
                {
                    "task_id": idx,
                    "error": str(e),
                    "failed": True,
                }
            )

        # Checkpoint after each idx
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

    successful = len([r for r in results if not r.get("failed", False)])
    print(f"\nCompleted: {successful}/{len(results)} tasks successfully generated")
    print(f"Saved to {out_p}")


if __name__ == "__main__":
    main()
