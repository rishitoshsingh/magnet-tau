from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any, Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from emotions.emotion_instruction_prompts import (
    BLEND_SYSTEM_PROMPT,
    INSTRUCTION_SYSTEM_PROMPT,
)

load_dotenv()


class SubCategory(BaseModel):
    name: str
    definition: str


class EmotionCategory(BaseModel):
    category: str
    sub_categories: list[SubCategory]


class EmotionBank(BaseModel):
    categories: list[EmotionCategory]


class BlendCandidate(BaseModel):
    blend: list[str] = Field(
        ...,
        description="A valid same-time blend of sub-category emotions from one top-level category.",
    )
    rationale: str = Field(
        ...,
        description="Short reason these emotions can realistically co-exist in the same interaction.",
    )


class BlendSelection(BaseModel):
    blends: list[BlendCandidate] = Field(
        ...,
        description="Valid emotion blends for one category. Avoid incompatible or redundant combinations.",
    )


class InstructionBatch(BaseModel):
    instructions: list[str] = Field(
        ...,
        description="Distinct user-side persona instructions, each 2-3 lines, meant to be appended to a customer-service task prompt.",
    )


class WorkflowState(TypedDict):
    category_index: int
    blend_index: int
    current_category: dict[str, Any] | None
    current_blends: list[dict[str, Any]]
    current_output_category: dict[str, Any] | None
    output_categories: list[dict[str, Any]]


def _sanitize_temperature(model: str, temperature: float) -> float:
    if model.startswith("gpt-5"):
        return 1.0
    return temperature


def _make_chat_model(provider: str, model: str, temperature: float, base_api: str | None) -> ChatOpenAI:
    provider = provider.lower()
    temperature = _sanitize_temperature(model, temperature)

    if provider == "openai":
        return ChatOpenAI(model=model, temperature=temperature, max_retries=2)

    if provider in {"vllm", "openai-compatible", "openai_compatible"}:
        if not base_api:
            raise ValueError("For provider 'vllm' or 'openai-compatible', you must supply --base-api.")
        api_key = (
            os.getenv("OPENAI_COMPATIBLE_API_KEY")
            or os.getenv("VLLM_API_KEY")
            or "EMPTY"
        )
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            max_retries=2,
            base_url=base_api,
            api_key=api_key,
        )

    if provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY", "EMPTY")
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            max_retries=2,
            base_url=base_api or "https://api.deepseek.com/v1",
            api_key=api_key,
        )

    raise ValueError(f"Unsupported provider: {provider}")


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _dedupe_preserve_order(blends: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, ...]] = set()
    deduped: list[dict[str, Any]] = []
    for blend in blends:
        key = tuple(blend["blend"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(blend)
    return deduped


def _normalize_blends(
    raw_blends: list[BlendCandidate],
    category: EmotionCategory,
    max_blends: int,
) -> list[dict[str, Any]]:
    allowed_names = {sub.name for sub in category.sub_categories}
    normalized: list[dict[str, Any]] = []

    for item in raw_blends:
        cleaned: list[str] = []
        for emotion in item.blend:
            lowered = emotion.strip().lower()
            if lowered in allowed_names and lowered not in cleaned:
                cleaned.append(lowered)

        if not cleaned:
            continue

        if len(cleaned) > 4:
            cleaned = cleaned[:4]

        normalized.append(
            {
                "blend": cleaned,
                "rationale": item.rationale.strip(),
            }
        )

    normalized = _dedupe_preserve_order(normalized)

    # Guarantee minimum coverage when the requested maximum allows it.
    target_minimum = min(len(category.sub_categories), max_blends)
    if len(normalized) < target_minimum:
        existing = {tuple(item["blend"]) for item in normalized}
        for sub in category.sub_categories:
            candidate = (sub.name,)
            if candidate in existing:
                continue
            normalized.append(
                {
                    "blend": [sub.name],
                    "rationale": f"Single-emotion baseline blend for {sub.name}.",
                }
            )
            existing.add(candidate)
            if len(normalized) >= target_minimum:
                break

    return normalized[:max_blends]


def _load_reference_examples(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}

    with path.open() as f:
        data = json.load(f)

    examples: dict[str, list[str]] = {}
    for category in data.get("categories", []):
        name = str(category.get("category", "")).lower()
        texts = [
            instruction.get("text", "").strip()
            for instruction in category.get("instructions", [])
            if instruction.get("text")
        ]
        if texts:
            examples[name] = texts[:2]
    return examples


def _load_config_defaults(config_path: str) -> dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _resolve_graph_png_path(output_path: Path, graph_png_path: str | None) -> Path:
    if graph_png_path:
        return Path(graph_png_path)
    return output_path.with_name(f"{output_path.stem}.graph.png")


def _write_graph_png(workflow: "EmotionInstructionWorkflow", graph_png_path: Path) -> None:
    graph_png_path.parent.mkdir(parents=True, exist_ok=True)
    png_bytes = workflow.graph.get_graph().draw_mermaid_png()
    graph_png_path.write_bytes(png_bytes)


class EmotionInstructionWorkflow:
    def __init__(
        self,
        model: str,
        temperature: float,
        provider: str,
        base_api: str | None,
        max_blends: int,
        instructions_per_blend: int,
        emotion_bank_path: Path,
        recursion_limit: int | None = None,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.provider = provider
        self.base_api = base_api
        self.max_blends = max_blends
        self.instructions_per_blend = instructions_per_blend
        self.emotion_bank_path = emotion_bank_path

        with emotion_bank_path.open() as f:
            self.emotion_bank = EmotionBank.model_validate(json.load(f))

        self.reference_examples = _load_reference_examples(
            emotion_bank_path.with_name("emotion_instructions.json")
        )
        self.recursion_limit = recursion_limit or self._default_recursion_limit()
        self.blend_chain = self._build_blend_chain()
        self.instruction_chain = self._build_instruction_chain()
        self.graph = self._build_graph()

    def _log(self, message: str) -> None:
        print(message, flush=True)

    def _default_recursion_limit(self) -> int:
        # Per category we traverse:
        # load_category -> generate_blends -> generate_instructions * blends -> finalize_category
        # Add generous buffer for safety.
        category_count = len(self.emotion_bank.categories)
        return category_count * (self.max_blends + 4) + 25

    def _build_blend_chain(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", BLEND_SYSTEM_PROMPT),
                (
                    "human",
                    """Top-level category: {category}
Requested maximum number of blends: {max_blends}

Sub-category bank:
{sub_category_bank}

Return realistic blends for customer-service interactions. The full set should be diverse and cover the category well.
""",
                ),
            ]
        )
        model = _make_chat_model(
            provider=self.provider,
            model=self.model,
            temperature=self.temperature,
            base_api=self.base_api,
        ).with_structured_output(BlendSelection)
        return prompt | model

    def _build_instruction_chain(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", INSTRUCTION_SYSTEM_PROMPT),
                (
                    "human",
                    """Top-level category: {category}
Blend: {blend}
Requested number of instruction variants: {num_variants}

Definitions for this blend:
{blend_definitions}

Reference examples from an older instruction file for style only:
{reference_examples}

Generate exactly {num_variants} distinct instruction variants for this blend.
""",
                ),
            ]
        )
        model = _make_chat_model(
            provider=self.provider,
            model=self.model,
            temperature=self.temperature,
            base_api=self.base_api,
        ).with_structured_output(InstructionBatch)
        return prompt | model

    def _build_graph(self):
        builder = StateGraph(WorkflowState)
        builder.add_node("load_category", self._load_category)
        builder.add_node("generate_blends", self._generate_blends)
        builder.add_node("generate_instructions", self._generate_instructions)
        builder.add_node("finalize_category", self._finalize_category)

        builder.set_entry_point("load_category")
        builder.add_edge("load_category", "generate_blends")
        builder.add_edge("generate_blends", "generate_instructions")
        builder.add_conditional_edges(
            "generate_instructions",
            self._route_after_instruction,
            {
                "generate_instructions": "generate_instructions",
                "finalize_category": "finalize_category",
            },
        )
        builder.add_conditional_edges(
            "finalize_category",
            self._route_after_category,
            {
                "load_category": "load_category",
                END: END,
            },
        )
        return builder.compile()

    def _load_category(self, state: WorkflowState) -> WorkflowState:
        category = self.emotion_bank.categories[state["category_index"]]
        self._log(
            f'Working on emotion "{category.category}" '
            f'({state["category_index"] + 1}/{len(self.emotion_bank.categories)})'
        )
        return {
            **state,
            "blend_index": 0,
            "current_category": category.model_dump(),
            "current_blends": [],
            "current_output_category": {
                "category": category.category,
                "coverage": [sub.name for sub in category.sub_categories],
                "blends": [],
            },
        }

    def _generate_blends(self, state: WorkflowState) -> WorkflowState:
        category = EmotionCategory.model_validate(state["current_category"])
        e_count = len(category.sub_categories)
        sub_category_bank = "\n".join(
            f"- {sub.name}: {sub.definition}" for sub in category.sub_categories
        )

        self._log(
            f'Agent 1: Generating blends for "{category.category}" '
            f"(E={e_count}, M={self.max_blends})..."
        )

        response = self.blend_chain.invoke(
            {
                "category": category.category,
                "max_blends": self.max_blends,
                "sub_category_bank": sub_category_bank,
            }
        )

        normalized = _normalize_blends(response.blends, category, self.max_blends)
        self._log(
            f'Agent 1: Found {len(normalized)} blends for "{category.category}".'
        )
        return {
            **state,
            "current_blends": normalized,
            "blend_index": 0,
        }

    def _generate_instructions(self, state: WorkflowState) -> WorkflowState:
        category = EmotionCategory.model_validate(state["current_category"])
        blend_payload = state["current_blends"][state["blend_index"]]
        lookup = {sub.name: sub.definition for sub in category.sub_categories}
        blend = blend_payload["blend"]
        blend_definitions = "\n".join(f"- {name}: {lookup[name]}" for name in blend)
        blend_text = "+".join(blend)

        self._log(
            f'Agent 2: Generating instructions for emotion "{category.category}" '
            f'+ blend "{blend_text}" '
            f'({state["blend_index"] + 1}/{len(state["current_blends"])})...'
        )

        examples = self.reference_examples.get(category.category, [])
        if examples:
            formatted_examples = "\n\n".join(
                f"Example {idx + 1}:\n{text}" for idx, text in enumerate(examples)
            )
        else:
            formatted_examples = "No reference examples available."

        instructions = self._generate_instruction_variants(
            category=category.category,
            blend=blend,
            blend_definitions=blend_definitions,
            reference_examples=formatted_examples,
        )

        current_output_category = dict(state["current_output_category"] or {})
        current_blends = list(current_output_category.get("blends", []))
        blend_id = f"{_slug(category.category)}_blend_{state['blend_index'] + 1}"
        current_blends.append(
            {
                "id": blend_id,
                "blend": blend,
                "rationale": blend_payload["rationale"],
                "instructions": [
                    {
                        "id": f"{blend_id}_instruction_{idx + 1}",
                        "text": text,
                    }
                    for idx, text in enumerate(instructions)
                ],
            }
        )
        current_output_category["blends"] = current_blends

        return {
            **state,
            "blend_index": state["blend_index"] + 1,
            "current_output_category": current_output_category,
        }

    def _generate_instruction_variants(
        self,
        category: str,
        blend: list[str],
        blend_definitions: str,
        reference_examples: str,
    ) -> list[str]:
        last_result: list[str] = []
        for _ in range(3):
            response = self.instruction_chain.invoke(
                {
                    "category": category,
                    "blend": ", ".join(blend),
                    "num_variants": self.instructions_per_blend,
                    "blend_definitions": blend_definitions,
                    "reference_examples": reference_examples,
                }
            )
            cleaned = [item.strip() for item in response.instructions if item.strip()]
            deduped = list(dict.fromkeys(cleaned))
            last_result = deduped[: self.instructions_per_blend]
            if len(last_result) == self.instructions_per_blend:
                return last_result

        raise ValueError(
            f"Instruction agent returned {len(last_result)} instructions for blend {blend}, "
            f"expected {self.instructions_per_blend}."
        )

    def _finalize_category(self, state: WorkflowState) -> WorkflowState:
        output_categories = list(state["output_categories"])
        output_categories.append(state["current_output_category"])
        category_name = (state["current_output_category"] or {}).get("category", "unknown")
        self._log(f'Finished emotion "{category_name}".')
        return {
            **state,
            "category_index": state["category_index"] + 1,
            "current_category": None,
            "current_blends": [],
            "current_output_category": None,
            "output_categories": output_categories,
        }

    def _route_after_instruction(self, state: WorkflowState) -> Literal["generate_instructions", "finalize_category"]:
        if state["blend_index"] < len(state["current_blends"]):
            return "generate_instructions"
        return "finalize_category"

    def _route_after_category(self, state: WorkflowState) -> Literal["load_category", END]:
        if state["category_index"] < len(self.emotion_bank.categories):
            return "load_category"
        return END

    def run(self) -> dict[str, Any]:
        self._log(f"Using LangGraph recursion_limit={self.recursion_limit}")
        final_state = self.graph.invoke(
            {
                "category_index": 0,
                "blend_index": 0,
                "current_category": None,
                "current_blends": [],
                "current_output_category": None,
                "output_categories": [],
            },
            config={"recursion_limit": self.recursion_limit},
        )
        return {
            "version": "2.0",
            "interpretation": (
                "User-side persona instructions grouped by top-level emotion category and by "
                "valid same-time emotion blend. Each instruction is meant to be appended to a "
                "base customer-service task prompt."
            ),
            "schema": {
                "unit": "emotion instruction block",
                "line_count": "2-3 lines",
                "usage": "Append one instruction block to a base task prompt for the user LLM.",
                "fields": ["id", "text"],
                "blend_container_fields": ["id", "blend", "rationale", "instructions"],
            },
            "generation_config": {
                "model": self.model,
                "temperature": _sanitize_temperature(self.model, self.temperature),
                "provider": self.provider,
                "base_api": self.base_api,
                "max_blends": self.max_blends,
                "instructions_per_blend": self.instructions_per_blend,
                "emotion_bank_path": str(self.emotion_bank_path),
                "recursion_limit": self.recursion_limit,
            },
            "categories": final_state["output_categories"],
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build blended emotion instructions with a two-agent LangGraph workflow."
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to JSON config file. Config keys override script defaults; CLI overrides config.",
    )
    parser.add_argument("--model", default=None, help="Model name to use for both agents.")
    parser.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature.")
    parser.add_argument(
        "--provider",
        default="openai",
        help="LLM provider: openai | vllm | openai-compatible | deepseek",
    )
    parser.add_argument(
        "--base-api",
        dest="base_api",
        default=None,
        help="Base URL for OpenAI-compatible providers such as vLLM.",
    )
    parser.add_argument(
        "--max-blends",
        type=int,
        default=None,
        help="Maximum number of emotion blends to keep per top-level category.",
    )
    parser.add_argument(
        "--instructions-per-blend",
        type=int,
        default=None,
        help="Number of instruction variants to generate for each accepted blend.",
    )
    parser.add_argument(
        "--emotion-bank-path",
        "--json-file-path",
        dest="emotion_bank_path",
        default=None,
        help="Path to the emotion bank JSON file.",
    )
    parser.add_argument(
        "--output-path",
        default="emotions/emotion_instructions.generated.json",
        help="Where to write the generated instruction JSON.",
    )
    parser.add_argument(
        "--graph-png-path",
        default=None,
        help="Optional path for the workflow graph PNG. Defaults to the output JSON folder.",
    )
    parser.add_argument(
        "--recursion-limit",
        type=int,
        default=None,
        help="Optional LangGraph recursion limit override. By default, a safe value is computed from category count and max blends.",
    )

    args_pre, _ = parser.parse_known_args()
    if args_pre.config is not None:
        cfg = _load_config_defaults(args_pre.config)
        for action in parser._actions:
            if action.dest != "config" and action.dest in cfg:
                action.default = cfg[action.dest]

    args = parser.parse_args()

    required_fields = ["model", "max_blends", "instructions_per_blend", "emotion_bank_path"]
    missing_fields = [field for field in required_fields if getattr(args, field) in (None, "")]
    if missing_fields:
        parser.error(
            "Missing required arguments after applying config/CLI merge: "
            + ", ".join(f"--{field.replace('_', '-')}" for field in missing_fields)
        )

    return args


def main() -> None:
    args = parse_args()

    workflow = EmotionInstructionWorkflow(
        model=args.model,
        temperature=args.temperature,
        provider=args.provider,
        base_api=args.base_api,
        max_blends=args.max_blends,
        instructions_per_blend=args.instructions_per_blend,
        emotion_bank_path=Path(args.emotion_bank_path),
        recursion_limit=args.recursion_limit,
    )
    result = workflow.run()

    output_path = Path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")

    graph_png_path = _resolve_graph_png_path(output_path, args.graph_png_path)
    _write_graph_png(workflow, graph_png_path)

    print(f"Wrote emotion instructions to {output_path}")
    print(f"Wrote workflow graph PNG to {graph_png_path}")


if __name__ == "__main__":
    main()
