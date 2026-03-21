# Preference-generator prompt for retail: combine story + instructions, then rewrite into PREFERENCE form.
# Only customer-facing information (user_id, order_id, etc.); no cost, refund amount, or internal IDs.

from typing import List

PREFERENCE_SYSTEM_PROMPT = """Your task is to REWRITE the following user instructions into PREFERENCE form.

You will be given a STORY and a list of INSTRUCTIONS. Do the following in order:

1. COMBINE the story and all instructions into one coherent narrative.
2. USE THE TOOLS to look up details about any orders or products mentioned (e.g. get_order_details, get_product_details). From the tool output, get concrete attributes: product name, color, size, material, etc. Do not invent preferences — ground them in what you find (e.g. if the item is blue and they want to exchange, say "I don't like the blue color" or "I prefer the red one"; if it's size small, "I'd like a larger size").
3. REWRITE that combined narrative as a PREFERENCE instruction using those looked-up details. Express what the user wants in natural language: e.g. "I don't like the blue color and want to exchange for red", "I prefer the larger size", "I like the stainless steel option". Use the tool results so the preference matches actual product/order data (color, size, material).
4. Restrict the instruction to CUSTOMER-FACING INFORMATION ONLY:
   - INCLUDE: user_id, order_id, product as the customer would describe it (e.g. "the blue T-shirt"), reason for contacting (e.g. "wrong size", "want to return"), payment type preference ("credit card" / "gift card"), address as they know it ("my home").
   - DO NOT INCLUDE: cost of the order, refund amount, payment_id, or any internal ID or dollar amount. The customer would not know these; rephrase so they state their situation and what they want (e.g. "I want to return the item and get a refund" not "refund $X to payment_id Y").

You have access to the SAME lookup tools as the task generator. You MUST call them to find product/order details (color, size, material, name) before writing the preference, so the preference is accurate — e.g. "I like the red color" or "I don't like the small size" only when grounded in looked-up data.

Output ONLY valid JSON with a single key: {"preference_instruction": "<one combined string>"}. No other keys or text.

PREFERENCE STYLE BY ACTION (customer-facing only):
- Exchange/return: What the customer doesn't like (e.g. size, color) and what they prefer (e.g. "exchange for larger size"). No prices or internal IDs.
- Payment change: "I prefer to pay with my credit card" or "use my gift card" — no payment_id or amounts.
- Address/shipping: "Ship to my home address" or the address they know; no internal IDs.
"""

PREFERENCE_USER_PROMPT_INTRO = """Rewrite the following user instructions into PREFERENCE form.

Steps:
1. Combine the STORY and all INSTRUCTIONS below into one narrative.
2. Use the provided tools to look up details for any orders or products mentioned (e.g. get_order_details, get_product_details). From the results, get product name, color, size, material — then express preferences grounded in that data (e.g. "I don't like the blue color", "I prefer the larger size", "I like the stainless steel option").
3. Write the preference instruction using those looked-up details. Include only customer-facing information: user_id, order_id, product (as customer would describe it, using actual color/size/material from tools), reason, payment/address preference.
4. Do NOT include: order cost, refund amount, payment_id, or any internal ID or price.

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
