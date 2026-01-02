from typing import Any, Dict

from tau_bench.envs.telehealth.tools.get_regimen_options import (
    GetRegimenOptions as _GetRegimenOptions,
)


class GetRegimenOptions(_GetRegimenOptions):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_regimen_options",
                "description": (
                    "Retrieve the current medication regimen and optimized alternative regimen options for a patient. "
                    "Includes component-level details (medication, dosage, unit cost, supplier), overall pill burden, "
                    "and any synergy/clinical notes for each optimized option. Returns a human-readable multi-line "
                    "string or an error message if no regimen data is available."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "patient_id": {
                            "type": "string",
                            "description": (
                                "ID of the patient, such as 'sarah_johnson_1234'. "
                                "Must correspond to a key in the 'regimen_plans' map."
                            ),
                        },
                    },
                    "required": ["patient_id"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "Multi-line, human-readable summary of the patient's current regimen and optimized regimen "
                        "options, or an error string if no regimen optimization data exists for the patient. "
                        "The format includes:\n"
                        "- Current regimen components (one per line)\n"
                        "- Current pill burden (tablets per day, devices per month)\n"
                        "- Current regimen notes (if present)\n"
                        "- Optimized options with name, focus, components, pill burden, and synergy notes"
                    ),
                    "examples": [
                        # Successful example for sarah_johnson_1234
                        (
                            "Current regimen components:\n"
                            "- Metformin | dosage=500mg | daily_dose=2 | monthly_units=60 | unit_type=tablet | "
                            "brand=Glucophage | supplier=PharmaCo USA | unit_cost_usd=0.45\n"
                            "- Lisinopril | dosage=10mg | daily_dose=1 | monthly_units=30 | unit_type=tablet | "
                            "brand=Prinivil | supplier=MedSupply Inc | unit_cost_usd=0.30\n"
                            "Current pill burden: tablets_per_day=3 | devices_per_month=0\n"
                            "Current regimen notes:\n"
                            "  * Taking medications twice daily\n"
                            "  * No reported side effects\n"
                            "  * Good adherence per patient report\n"
                            "Optimized regimen options:\n"
                            "Option 1: Extended Release Option\n"
                            "  Focus: Reduced pill burden with extended-release formulation\n"
                            "  - Metformin ER | dosage=1000mg | daily_dose=1 | monthly_units=30 | unit_type=tablet | "
                            "brand=Glucophage XR | supplier=PharmaCo USA | unit_cost_usd=0.85\n"
                            "  - Lisinopril | dosage=10mg | daily_dose=1 | monthly_units=30 | unit_type=tablet | "
                            "brand=Prinivil | supplier=MedSupply Inc | unit_cost_usd=0.30\n"
                            "  Pill burden: tablets_per_day=2 | devices_per_month=0\n"
                            "  Synergy notes:\n"
                            "    - Single daily Metformin dose improves adherence\n"
                            "    - Reduced GI side effects with extended release\n"
                            "    - Same efficacy as current regimen\n"
                            "Option 2: Cost-Optimized Generic\n"
                            "  Focus: Lower cost with generic alternatives\n"
                            "  - Metformin | dosage=500mg | daily_dose=2 | monthly_units=60 | unit_type=tablet | "
                            "brand=Generic | supplier=ValueMeds Direct | unit_cost_usd=0.18\n"
                            "  - Lisinopril | dosage=10mg | daily_dose=1 | monthly_units=30 | unit_type=tablet | "
                            "brand=Generic | supplier=ValueMeds Direct | unit_cost_usd=0.12\n"
                            "  Pill burden: tablets_per_day=3 | devices_per_month=0\n"
                            '  Synergy notes:\n'
                            "    - Significant cost savings\n"
                            "    - Same active ingredients as brand\n"
                            "    - FDA-approved bioequivalent formulations"
                        ),
                        # Error case example
                        "No regimen optimization data available for patient unknown_patient_9999.",
                    ],
                },
            },
        }