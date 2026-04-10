from typing import List

# Preference-generator prompt for telehealth: combine story + instructions, then rewrite into PREFERENCE form.
# Only patient-facing information (patient_id, appointment_id, provider names, medications as they'd describe them);
# no copay amounts, voucher IDs, internal record IDs beyond what a patient would see, or billing details.

PREFERENCE_SYSTEM_PROMPT = """Your task is to REWRITE the following telehealth user instructions into PREFERENCE form.

You will be given a STORY and a list of INSTRUCTIONS. Do the following in order:

1. COMBINE the story and all instructions into one coherent narrative.
2. USE THE TOOLS to look up details about any appointments, providers, medical records, medications, or devices mentioned
   (e.g. get_appointment_details, get_provider_details, get_medical_record, get_patient_details_complete,
   list_medication_suppliers, check_drug_interactions). From the tool output, get concrete attributes:
   appointment dates/times, visit type, provider specialty, medication names, formulation, dosage, device type, etc.
   Do not invent preferences — ground them in what you find (e.g. if an appointment is early morning, say
   "I prefer a later morning slot"; if the medication is a pill taken twice daily, say "I'd prefer a once-daily option").
3. REWRITE that combined narrative as a PREFERENCE instruction using those looked-up details. Express what the patient wants
   in natural language: e.g. "I prefer afternoon appointments with my cardiologist", "I don't like taking this pill twice a day
   and would prefer a once-daily option", "I prefer using a wearable patch instead of a finger-clip device".
   Use the tool results so the preference matches actual appointment/medication/device data.
4. Restrict the instruction to PATIENT-FACING INFORMATION ONLY:
   - INCLUDE: patient_id (or how they self-identify), appointment_id(s), provider names/specialties as a patient would say
     them, basic medication names and schedules ("this blood pressure pill twice a day"), device descriptions
     ("the wrist blood pressure cuff"), high-level reasons for contacting (e.g. "too early in the morning", "too many pills",
     "device is uncomfortable"), and high-level billing preferences ("I'd like it billed to my insurance" vs "I'd rather self-pay").
   - DO NOT INCLUDE: exact copay amounts, voucher IDs, internal payment IDs, insurance authorization numbers, internal
     record IDs beyond what a patient would reasonably know, or any dollar amounts. Rephrase so the patient states their
     situation and what they want (e.g.      "I'd like to cancel this appointment and avoid a cancellation fee" not
     "cancel and waive a $25 fee").

ORDER OF REQUESTS: The INSTRUCTIONS are numbered in the order the patient stated their asks. Your single `preference_instruction` must follow that same order: cover what instruction 1 asks for first, then instruction 2, then 3, and so on. You may use natural connectors between sentences, but do not reorder requests (never put a later instruction's ask before an earlier one).

You have access to the SAME lookup tools as the task generator. You MUST call them to find appointment/provider/record
details before writing the preference, so the preference is accurate — e.g. "I prefer afternoon visits" only if the
existing or candidate appointments show different times of day.

Output ONLY valid JSON with a single key: {"preference_instruction": "<one combined string>"}. No other keys or text.

PREFERENCE STYLE BY ACTION (patient-facing only):
- Appointment scheduling/rescheduling/cancellation: What the patient likes or dislikes about times, days, provider specialty,
  virtual vs in-person, etc. (e.g. "I prefer evening video visits with my primary care doctor").
- Medication/regimen changes: What the patient prefers about dosing schedule, formulation, or supplier
  (e.g. "I'd prefer a once-daily pill instead of twice daily", "I'd like to use the lower-cost pharmacy option").
- Telemetry/devices: What the patient prefers about device form factor or usage (e.g. "I prefer a wrist cuff instead of
  a finger clip", "I'd like a device I can wear overnight comfortably").
"""

PREFERENCE_USER_PROMPT_INTRO = """Rewrite the following telehealth user instructions into PREFERENCE form.

Steps:
1. Combine the STORY and all INSTRUCTIONS below into one narrative.
2. Use the provided tools to look up details for any appointments, providers, medical records, medications, or devices
   mentioned (e.g. get_appointment_details, get_provider_details, get_medical_record, list_medication_suppliers,
   check_drug_interactions). From the results, get visit dates/times, provider specialties, medication names/schedules,
   and device types — then express preferences grounded in that data (e.g. "I prefer afternoon appointments",
   "I prefer a once-daily pill", "I prefer a different type of monitoring device").
3. Write the preference instruction using those looked-up details. Include only patient-facing information:
   patient_id/identity, appointment_id(s), provider names/specialties, medication descriptions and schedules as they
   would describe them, device descriptions, and high-level billing/insurance preferences. Keep the same order of requests as the numbered INSTRUCTIONS (first instruction first, then the next).
4. Do NOT include: copay amounts, voucher IDs, internal payment IDs, insurance authorization numbers, or any exact prices.

STORY (context): {story}

INSTRUCTIONS (one per line):
{instructions}

When done, respond with ONLY a JSON object: {{"preference_instruction": "<one combined string>"}}"""


def format_preference_user_prompt(story: str, instructions: List[str]) -> str:
    """Build the user prompt (initial observation) for the telehealth preference agent."""
    story_part = story or ""
    instructions_part = "\n".join(f"{i+1}. {inst}" for i, inst in enumerate(instructions))
    return PREFERENCE_USER_PROMPT_INTRO.format(
        story=story_part,
        instructions=instructions_part,
    )

