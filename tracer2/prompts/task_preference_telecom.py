# Preference-generator prompt for telecom: combine story + instructions, then rewrite into PREFERENCE form.

from typing import List

PREFERENCE_SYSTEM_PROMPT = """Your task is to REWRITE the following user instructions into PREFERENCE form.

You will be given a STORY and a list of INSTRUCTIONS. Do the following in order:

1. COMBINE the story and all instructions into one coherent narrative.
2. USE THE TOOLS to look up relevant details about the customer or services mentioned (e.g. get_customer_details, get_service_details, get_billing_details). From the tool output, get concrete attributes: which services they're on, device names, billing preferences, ticket status — so you can express preferences grounded in real data (e.g. "I'd like to switch to a fiber plan", "I prefer paperless billing").
3. REWRITE that combined narrative as a PREFERENCE instruction using those looked-up details. Express what the user wants in natural language: e.g. "I prefer to manage everything online", "I'd like a plan with faster internet", "I want my billing sent to my email". Use the tool results so the preference matches actual customer/service data.
4. Restrict the instruction to CUSTOMER-FACING INFORMATION ONLY:
   - INCLUDE: customer_id, service names (not raw service_ids), device names, ticket references, issue descriptions, billing preferences.
   - Do NOT include: raw service_ids (e.g. "mobile_unlimited") — use the human-readable name instead (e.g. "Unlimited Mobile Plan"). Do NOT include internal system IDs or exact balance amounts unless the customer would naturally state them.
   - Do NOT include: internal tool names or reverse tool outputs.

ORDER OF REQUESTS: The INSTRUCTIONS are numbered in the order the user stated their asks. Your single `preference_instruction` must follow that same order: cover what instruction 1 asks for first, then instruction 2, then 3, and so on. You may use natural connectors between sentences, but do not reorder requests.

You have access to the SAME lookup tools as the task generator. You MUST call them to find relevant details before writing the preference, so it is accurate and grounded.

Output ONLY valid JSON with a single key: {"preference_instruction": "<one combined string>"}. No other keys or text.

Example: "I'm john_smith_1234. My iPhone 15 Pro has been having battery issues and I'd like help troubleshooting it. After that, I'd like to open a support ticket for the device issue and escalate it to high priority."
"""

PREFERENCE_USER_PROMPT_INTRO = """Rewrite the following user instructions into PREFERENCE form.

Steps:
1. Combine the STORY and all INSTRUCTIONS below into one narrative.
2. Use the provided tools to look up relevant details for any customer, service, or device mentioned (e.g. get_customer_details, get_service_details, get_billing_details). From the results, get service names, device names, billing status — then express preferences grounded in that data.
3. Write the preference instruction using those looked-up details. Include only customer-facing information: customer_id, human-readable service names, device names, issue descriptions, ticket references. Keep the same order of requests as the numbered INSTRUCTIONS.
4. Do not paste raw service_ids or internal identifiers — use human-readable names from tool outputs.

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
