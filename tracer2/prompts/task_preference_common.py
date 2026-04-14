from __future__ import annotations

from typing import Iterable

PREFERENCE_JSON_CONTRACT = (
    'Output ONLY valid JSON with a single key: {"preference_instruction": "<one combined string>"}. '
    "No other keys or text."
)

COMMON_SYSTEM_PROMPT_CORE = """You will be given a STORY and a list of INSTRUCTIONS. Do the following in order:

1. COMBINE the story and all instructions into one coherent narrative.
2. USE THE TOOLS to look up details for any concrete entities or IDs mentioned in the instructions.
   Use tool outputs to ground facts and map internal identifiers to customer-facing language.
   Do not copy raw tool outputs, backend dumps, or procedural troubleshooting steps into the final instruction.
3. REWRITE that combined narrative as a single PREFERENCE instruction in natural language.
   For each main ask or preference, include a short why-clause grounded in the STORY/INSTRUCTIONS or tool facts.
   Do not invent unrelated backstory.
4. Preserve ORDER OF REQUESTS: follow the original numbered instruction order exactly.
   - If a later instruction changes direction (e.g. update first, then cancel), keep both asks in sequence.
   - Use transition language that preserves chronology (e.g. later, after that, subsequently) and contextual motivation.
   - Do not rewrite chronology as contradiction framing (e.g. "instead of the first ask") unless the source explicitly says to replace/override the earlier ask.
5. Keep the result customer-facing and avoid internal identifiers or system-only jargon.
6. Write in THIRD-PERSON instruction style.
   - The combined preference instruction must be phrased as guidance to an agent, not a first-person customer quote.
   - Start the instruction with "You are ..." and continue in that same third-person/instructional style.

When expressing asks, use clear preference/request wording in third-person instructional voice (e.g. "You want...", "You would like...", "You prefer...").
"""

COMMON_USER_PROMPT_STEPS = """Steps:
1. Combine the STORY and all INSTRUCTIONS below into one narrative.
2. Use the provided tools to look up concrete details and map internal IDs into customer-facing language.
   Use tools for grounding, not for copying backend/procedural text into the final output.
3. Write one combined preference instruction with short grounded why-clauses for each main ask.
4. Keep the same order as the numbered INSTRUCTIONS; if direction changes later, narrate it as a chronological transition, not as a contradiction.
5. Write in third-person instructional style, starting with "You are ..."; do not write in first-person voice.
6. Return only the required JSON object."""


def _join_sections(sections: Iterable[str]) -> str:
    return "\n\n".join(section.strip() for section in sections if section and section.strip())


def build_system_prompt(*sections: str) -> str:
    return _join_sections([*sections, PREFERENCE_JSON_CONTRACT])


def build_user_prompt_intro(task_line: str, *sections: str) -> str:
    safe_contract = PREFERENCE_JSON_CONTRACT.replace("{", "{{").replace("}", "}}")
    body = _join_sections([task_line, COMMON_USER_PROMPT_STEPS, *sections, safe_contract])
    return (
        f"{body}\n\n"
        "STORY (context): {story}\n\n"
        "INSTRUCTIONS (one per line):\n"
        "{instructions}\n\n"
        'When done, respond with ONLY a JSON object: {{"preference_instruction": "<one combined string>"}}'
    )
