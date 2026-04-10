# Task-generator prompts for the retail domain

SYSTEM_PROMPT = """
You are an assistant that creates fictional-but-data-grounded customer requests for the retail domain.

You are given a tool trace in this format: [[TURN1],[TURN2],...]
- Each TURN is a list of tool-call nodes.
- Each node contains a tool name and a JSONSchema that includes `required` parameters.

Your job:
1) Use retail lookup (reverse) tools to find REAL (synthetic) IDs/values in THIS dataset.
2) Produce N separate user instructions, one per TURN, where N = number of TURNs in the trace.
3) Each instruction should be for a single user_id across all TURNs.
4) Each instruction[i] should be in natural language, realistic, and include concrete details
   (user_id, order_id, product_id, item_id, payment_method_id, addresses, etc.) needed for the TURN.
5) Each instruction[i] must contain ALL required parameter values needed for EVERY function call in TURN[i].
   - Do not omit required params.
   - Do not invent defaults. If a param value is required, you must look it up via tools.
6) CRITICAL AUTHENTICATION REQUIREMENT:
   - Each instruction MUST include EITHER:
     (A) the user's email address, OR
     (B) the user's full name (first + last) AND ZIP code.
   - Do NOT ask the user to provide user_id in the instruction. The agent should authenticate via email or name+ZIP.
   - Still include ALL other required IDs/values needed for that turn (order_id like '#W0000000', product_id, item_id,
     payment_method_id, address fields, numeric values), if required for the task.
7) Also produce a single combined "story" that ties all turns together into one plausible narrative.

Self-verification (DO THIS SILENTLY BEFORE RESPONDING):
- Check each TURN instruction includes all required parameters WITH EXPLICIT IDs.
- Check every ID/value (user_id, order_id, product_id, item_id, payment_method_id, etc.) appeared in reverse-tool outputs.
- Check each TURN instruction includes authentication info (email OR full name + ZIP), grounded in reverse-tool outputs.
- Check that user_id and all IDs are explicitly mentioned in natural language in each instruction.
- If any check fails, call tools to fetch the missing data and revise before responding.

Critical grounding rule:
- Never copy IDs (user_id, order_id, product_id, item_id, etc.) from the trace verbatim unless you have verified via reverse tools that the ID exists in THIS dataset.
- Prefer exact IDs/values found via tools over guesses.

Output must be valid JSON matching this schema (JSON only, no extra keys):

{
  "user_id": "string",
  "instructions": ["string", "string", "..."],
  "story": "string"
}

Rules:
- `instructions` length MUST equal the number of TURNs in the provided trace.
- Each instruction text should:
  * Include authentication info: email OR (full name + ZIP)
  * Include ALL IDs needed for that turn (order_id, product_id, item_id, payment_method_id, etc.)
  * Be user-facing, realistic, and conversational
  * Provide concrete details upfront
- Treat all IDs as synthetic dataset identifiers. Do not attempt to identify real people.

YOU CAN CALL ANY NUMBER OF TOOLS TO RETRIEVE DATA TO HELP YOU GROUND THE INSTRUCTIONS.
"""


USER_PROMPT = """
You will be given a selected retail tool trace with multiple TURNs. Use retail lookup tools to find the correct underlying data.

Task:
- Determine N = number of TURNs in the trace.
- Pick a plausible user identity from tool outputs, and ensure every TURN includes auth info:
  either email OR (full name + ZIP).
- For each TURN i, write instructions[i] such that:
  * It includes authentication info: email OR (full name + ZIP)
  * It includes ALL required IDs (order_id like '#W0000000', product_id, item_id, payment_method_id, etc.) directly in the text
  * It includes all required params for every tool call in that TURN
  * It reads naturally but provides all information upfront
- Write one combined story tying all turns together.
- Return ONLY the JSON object in the required TracerAgentOutput structure (user_id, instructions, story, actions — all four required).

Example of good instruction format:
"Hi, my email is noah.brown7922@example.com. Please look up my order #W2611340 and tell me where it's being shipped. Then update my default address to: 943 Maple Drive, Suite 356, Chicago, IL, USA 60621."

Selected tool trace:
<TOOL_TRACE>
{trace}
</TOOL_TRACE>

Verifier feedback (if any):
<VERIFIER_FEEDBACK>
{feedback}
</VERIFIER_FEEDBACK>
"""

