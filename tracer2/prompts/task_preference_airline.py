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

Identity and passenger details:
- INCLUDE: user_id, reservation_id/confirmation code, origin/destination, travel date(s), cabin preference, passenger count, and reason for contacting.
- INCLUDE passenger names when available from instructions.
- If passenger names are not already available, say passenger details should be in the user account or other reservations.

Scheduling preference wording:
- Express schedule details as date + timing preference windows (morning/afternoon/evening/overnight or between HH:MM-HH:MM).
- Prefer customer-facing timing phrasing (for example "early morning", "late evening", "overnight") over itinerary-style details.
- For any booking/rebooking/new-flight ask, ALWAYS include origin (from), destination (to), travel date, and a time or time-window in the final preference wording.
- Use flight lookup tools to verify how many viable flights match the requested route/date/time window before writing the final preference wording.
- Flight IDs/numbers are usually not customer-facing preference language; AVOID them by default.
- Include a specific flight number ONLY when disambiguation is required (multiple viable matches in the same date/time context), or when explicitly requested in source instructions.
- DO NOT include itinerary constructions with flight numbers plus exact departure/arrival timestamps unless explicitly requested.

Flight-number preference decision policy (follow in order):
1) Identify requested route, travel date, and requested time/time-window from story+instructions and tool-grounded flight data.
2) Count viable flights on that same route and travel date.
3) Narrow to flights in the requested time or closest matching window (for example around 03:00 AM).
4) If exactly one viable match exists in that route/date/window, use broad customer-facing time language (for example early morning, morning, afternoon, evening, late evening, overnight) and omit exact HH:MM.
5) If multiple viable matches exist in that same route/date/window, use explicit time in HH:MM format to disambiguate; include flight number only if HH:MM still does not uniquely identify the option.
6) If source instructions explicitly require a specific flight number, include it; otherwise ALWAYS prefer natural customer wording.
7) Final wording MUST remain customer-facing and MUST NOT assume the customer knows internal flight identifiers.

Payment and privacy constraints:
- Reframe payment routing in customer language (e.g. "card ending in 4242", "my Visa on file") only when backed by story/tools.
- When payment method context exists, phrase it as an explicit preference (e.g. "You prefer to pay by ...", "You prefer refunds back to ...").
- DO NOT include raw payment/system IDs or exact fare/refund/compensation dollar amounts.

""",
)

PREFERENCE_USER_PROMPT_INTRO = build_user_prompt_intro(
    "Rewrite the following user instructions into PREFERENCE form.",
    """Airline checklist:
- Look up flight/reservation details before writing preferences.
- Ground time-of-day/cabin/route preferences in tool data.
- Convert concrete schedule outputs into preference wording (e.g. "on YYYY-MM-DD", "morning flight", "between HH:MM-HH:MM").
- For booking/rebooking/new-flight asks, ALWAYS include from, to, date, and time/time-window in the final customer-facing preference instruction.
- Prefer customer-facing timing phrases (for example "early morning", "late evening") with date context instead of exact timestamps.
- Use HH:MM format only when multiple viable flights in the same route/date window require time-level disambiguation.
- Check tool results for the count of matching flights in the requested route/date/time window before choosing wording.
- ONLY include flight number when multiple viable options share the same date/time context and disambiguation is necessary, or when explicitly requested.
- DO NOT use itinerary-style phrasing with exact departure/arrival times or specific flight numbers unless the user explicitly asks for those exact details.
- Include passenger names; if missing, use account details lookups to fetch passenger information first.
- If later asks change direction (e.g. update then cancel), keep both in chronological sequence with transition language.
- Keep final wording in third-person instruction style that starts with "You are ...".
- Keep payment/refund phrasing customer-facing and DO NOT include exact dollar figures/internal IDs.
- If a payment option is relevant, include a clear payment-method preference sentence (e.g. "You prefer to pay by ...").""",
)


def format_preference_user_prompt(story: str, instructions: List[str]) -> str:
    """Build the user prompt (initial observation) for the preference agent."""
    story_part = story or ""
    instructions_part = "\n".join(f"{i+1}. {inst}" for i, inst in enumerate(instructions))
    return PREFERENCE_USER_PROMPT_INTRO.format(
        story=story_part,
        instructions=instructions_part,
    )
