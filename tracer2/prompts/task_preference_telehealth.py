from typing import List

from tracer2.prompts.task_preference_common import (
    COMMON_SYSTEM_PROMPT_CORE,
    build_system_prompt,
    build_user_prompt_intro,
)

PREFERENCE_SYSTEM_PROMPT = build_system_prompt(
    "Your task is to REWRITE the following telehealth user instructions into PREFERENCE form.",
    COMMON_SYSTEM_PROMPT_CORE,
    """Telehealth-specific grounding:
- Use tools such as get_appointment_details, get_provider_details, check_provider_appointment_slot, get_medical_record, get_patient_details_complete, list_medication_suppliers, and check_drug_interactions.
- Ground preferences in appointment/provider/medication/device facts from tools.
- For scheduling/rescheduling asks, only express preferred times that align with actual provider availability.

Patient-facing constraints:
- INCLUDE: authenticated patient email identity, patient identity, appointment references, provider names/specialties, medication/device descriptions, and high-level billing preference wording.
- DO NOT include exact copay amounts, voucher IDs, internal payment IDs, insurance authorization numbers, or other internal record identifiers.

Preference style by action:
- Scheduling: timing/day/provider modality preferences with brief grounded reasons.
- Regimen changes: dosing/formulation/supplier preferences with patient-appropriate rationale.
- Telemetry/devices: comfort and usability preferences grounded in context.""",
)

PREFERENCE_USER_PROMPT_INTRO = build_user_prompt_intro(
    "Rewrite the following telehealth user instructions into PREFERENCE form.",
    """Telehealth checklist:
- Look up appointment/provider/medication/device details before writing preferences.
- Keep the authenticated patient email identity present in patient-facing form.
- For new or moved visit times, align wording to bookable windows from provider schedule/slot checks.
- If later asks change direction, keep chronology explicit with transition language instead of contradiction framing.
- Keep final wording in third-person instruction style that starts with "You are ...".
- Keep output patient-facing and omit internal billing/auth identifiers or exact prices.""",
)


def format_preference_user_prompt(story: str, instructions: List[str]) -> str:
    """Build the user prompt (initial observation) for the telehealth preference agent."""
    story_part = story or ""
    instructions_part = "\n".join(f"{i+1}. {inst}" for i, inst in enumerate(instructions))
    return PREFERENCE_USER_PROMPT_INTRO.format(
        story=story_part,
        instructions=instructions_part,
    )

