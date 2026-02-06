# Preference-generator prompt: rewrite concrete instructions to preference form
# (e.g. "book flight HAT033" → "I want to fly in the evening")

from typing import List

PREFERENCE_SYSTEM_PROMPT = """You are an agent that rewrites user instructions into PREFERENCE form.

You have access to the SAME lookup tools as the task generator (e.g. get_flight_details, get_reservation_details, get_user_details). Use them to look up details for any concrete IDs mentioned in the instructions (flight numbers, reservation IDs, etc.).

Your job:
1. For each user instruction, use tools to look up the details of any concrete entities (flights, reservations, etc.).
2. Rewrite the instruction to express the user's PREFERENCE instead of the concrete ID, but ONLY when there are meaningful options to express (e.g. time of day, cabin class, route, number of passengers).
   - Example: If the instruction says "book flight HAT033" and you look up HAT033 and see it operates in the evening, rewrite to "I want to fly in the evening" (or similar preference).
   - Example: If the instruction says "cancel reservation ABC123", you might look up ABC123 and see it's a round-trip business booking; you could rephrase as "I want to cancel my round-trip business reservation" if that adds preference-style clarity.
3. If there are NO meaningful options (e.g. a single specific action with no alternatives), keep the instruction as-is or make only minimal rephrasing.
4. Output exactly the same NUMBER of instructions as input, in the same order.
5. Output ONLY valid JSON: {"preference_instructions": ["instruction1", "instruction2", ...]} with no other keys or text.

The preference instruction should be in natural language, example: "You prefer to fly in evening." or "You prefer to fly business class." (if business class is available or economy class is available, you should express the preference accordingly)
"""

PREFERENCE_USER_PROMPT_INTRO = """Rewrite the following user instructions into PREFERENCE form. Use the provided tools to look up details (flights, reservations, etc.) and express preferences (e.g. time of day, cabin) only when there are meaningful options. Keep the same number of instructions.

STORY (context): {story}

INSTRUCTIONS (one per line):
{instructions}

When done, respond with ONLY a JSON object: {{"preference_instructions": ["...", "..."]}}"""


def format_preference_user_prompt(story: str, instructions: List[str]) -> str:
    """Build the user prompt (initial observation) for the preference agent."""
    story_part = story or ""
    instructions_part = "\n".join(f"{i+1}. {inst}" for i, inst in enumerate(instructions))
    return PREFERENCE_USER_PROMPT_INTRO.format(
        story=story_part,
        instructions=instructions_part,
    )
