# Preference-generator prompt for airline: combine story + instructions, then rewrite into PREFERENCE form.
# Customer-facing info only: reframe internal IDs (e.g. payment_id) as what a real customer would say.

from typing import List

PREFERENCE_SYSTEM_PROMPT = """Your task is to REWRITE the following user instructions into PREFERENCE form.

You will be given a STORY and a list of INSTRUCTIONS. Do the following in order:

1. COMBINE the story and all instructions into one coherent narrative.
2. USE THE TOOLS to look up details about any flights or reservations mentioned (e.g. get_flight_details, get_reservation_details). From the tool output, get concrete attributes: departure/arrival time (so you can say "I like to fly in the evening" or "in the morning"), cabin, route, dates. Do not invent preferences — ground them in what you find (e.g. if the flight departs at 18:00, say "I prefer to fly in the evening").
3. REWRITE that combined narrative as a PREFERENCE instruction using those looked-up details. Express what the user wants in natural language: e.g. "I want to fly in the evening", "I prefer economy", "I'd like a morning flight from JFK to LAX". Use the tool results so the preference matches actual flight/reservation data (time of day, cabin, route).
4. Restrict the instruction to CUSTOMER-FACING INFORMATION ONLY:
   - INCLUDE: user_id, reservation_id (confirmation code), flight numbers, origin/destination, dates, cabin preference, passenger count, reason for contacting (e.g. "my flight was cancelled", "I want to change my trip").
   - Do NOT paste internal IDs (e.g. raw payment_id, opaque system IDs). If the story or tool output implies a specific payment method, REFRAME it the way a customer would: e.g. "the card ending in 4242", "my Visa on file", "the PayPal account I paid with" — only use last-four, card brand, or similar details when they appear in tool/story data; do not invent digits.
   - Do NOT include: exact fare/compensation/refund/certificate dollar amounts, or internal-only identifiers. The customer states their situation and what they want (e.g. "I'd like compensation for my cancelled flight" not "give me a $300 certificate").

ORDER OF REQUESTS: The INSTRUCTIONS are numbered in the order the user stated their asks. Your single `preference_instruction` must follow that same order: cover what instruction 1 asks for first, then instruction 2, then 3, and so on. You may use natural connectors between sentences, but do not reorder requests (never put a later instruction's ask before an earlier one).

You have access to the SAME lookup tools as the task generator. You MUST call them to find flight/reservation details (times, cabin, route) before writing the preference, so the preference is accurate — e.g. "I like to fly in the evening" only if the looked-up flight is in the evening.

Output ONLY valid JSON with a single key: {"preference_instruction": "<one combined string>"}. No other keys or text.

Example: "I'm [user_id]. My reservation [ABC123] had a cancelled flight and I'd like to be compensated. I paid with the card ending in 4242 and want the refund there. I also want to book a new flight from JFK to LAX in the evening, economy, for 2 passengers." (No raw payment_id; no exact dollar amounts.)
"""

PREFERENCE_USER_PROMPT_INTRO = """Rewrite the following user instructions into PREFERENCE form.

Steps:
1. Combine the STORY and all INSTRUCTIONS below into one narrative.
2. Use the provided tools to look up details for any flights or reservations mentioned (e.g. get_flight_details, get_reservation_details). From the results, get time of day, cabin, route — then express preferences grounded in that data (e.g. "I like to fly in the evening" if the flight is evening).
3. Write the preference instruction using those looked-up details (e.g. "I prefer evening flights", "I want economy"). Include only customer-facing information: user_id, reservation_id, flight numbers, route, dates, cabin, passenger count, reason for contacting. Keep the same order of requests as the numbered INSTRUCTIONS (first instruction first, then the next).
4. Do not paste payment_id or other internal IDs — rephrase payments as a customer would (e.g. "card ending in …", card brand) using details from tools/story when available. Do not include exact dollar amounts for fares, compensation, or refunds.

STORY (context): {story}

INSTRUCTIONS (one per line):
{instructions}

When done, respond with ONLY a JSON object: {{"preference_instruction": "<one combined string>"}}"""


def format_preference_user_prompt(story: str, instructions: List[str]) -> str:
    """Build the user prompt (initial observation) for the preference agent."""
    story_part = story or ""
    instructions_part = "\n".join(f"{i+1}. {inst}" for i, inst in enumerate(instructions))
    return PREFERENCE_USER_PROMPT_INTRO.format(
        story=story_part,
        instructions=instructions_part,
    )
