from typing import List

from tracer2.prompts.task_preference_common import (
    COMMON_SYSTEM_PROMPT_CORE,
    build_system_prompt,
    build_user_prompt_intro,
)

PREFERENCE_SYSTEM_PROMPT = build_system_prompt(
    "Your task is to REWRITE the following user instructions into PREFERENCE form.",
    COMMON_SYSTEM_PROMPT_CORE,
    """Airline-specific grounding:
- Use tools such as get_flight_details and get_reservation_details to derive route, time-of-day, cabin, dates, and passenger context.
- Use these looked-up attributes to express customer preferences naturally (e.g. evening vs morning, economy vs business).

Customer-facing constraints:
- INCLUDE: user_id, reservation_id/confirmation code, flight numbers, origin/destination, dates, cabin preference, passenger count, and reason for contacting.
- INCLUDE passenger names when available from instructions.
- If passenger names are not already available, just say passengers details should be in the user account or other reservations.
- REFRAME payment routing in customer language (e.g. "card ending in 4242", "my Visa on file") only when backed by story/tools.
- DO NOT include raw payment/system IDs or exact fare/refund/compensation dollar amounts.

Example: "You are [user_id]. Reservation [ABC123] had a cancelled flight, so you would like compensation because the trip was disrupted. The payment was made with a card ending in 4242 and the refund should go there since that is how it was paid. You also prefer booking a new flight from JFK to LAX in the evening, economy, for 2 passengers, because evening fits the travel day." """,
)

PREFERENCE_USER_PROMPT_INTRO = build_user_prompt_intro(
    "Rewrite the following user instructions into PREFERENCE form.",
    """Airline checklist:
- Look up flight/reservation details before writing preferences.
- Ground time-of-day/cabin/route preferences in tool data.
- Include passenger names; if missing, use account details lookups to fetch passenger information first.
- If later asks change direction (e.g. update then cancel), keep both in chronological sequence with transition language.
- Keep final wording in third-person instruction style that starts with "You are ...".
- Keep payment/refund phrasing customer-facing and avoid exact dollar figures/internal IDs.""",
)


def format_preference_user_prompt(story: str, instructions: List[str]) -> str:
    """Build the user prompt (initial observation) for the preference agent."""
    story_part = story or ""
    instructions_part = "\n".join(f"{i+1}. {inst}" for i, inst in enumerate(instructions))
    return PREFERENCE_USER_PROMPT_INTRO.format(
        story=story_part,
        instructions=instructions_part,
    )
