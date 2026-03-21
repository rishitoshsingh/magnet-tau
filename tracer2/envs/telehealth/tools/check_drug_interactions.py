from typing import Any, Dict

from tau_bench.envs.telehealth.tools.check_drug_interactions import (
    CheckDrugInteractions as _CheckDrugInteractions,
)


class CheckDrugInteractions(_CheckDrugInteractions):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "check_drug_interactions",
                "description": (
                    "Evaluate potential interactions between a primary medication and a patient’s current regimen "
                    "using the environment’s structured interaction data. "
                    "This is for simulation/training only and is not real-world medical advice."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "primary_medication": {
                            "type": "string",
                            "description": (
                                "The medication that was taken accidentally or requires review, such as 'Sertraline'."
                            ),
                        },
                        "current_medications": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "List of the patient’s active medications, such as ['Warfarin', 'Aspirin', 'Metoprolol']."
                            ),
                        },
                    },
                    "required": ["primary_medication", "current_medications"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "Returns a multi-line textual analysis. If interactions are found, the output includes:\n"
                        "- A header line 'Drug interaction analysis:'\n"
                        "- One line per interaction of the form:\n"
                        "  '<Drug A> + <Drug B>: severity=<severity>, risk_score=<score>, "
                        "overlap_hours=<hours>. <recommended action>'\n"
                        "- A summary block with medications to hold, whether emergency escalation is required, "
                        "the peak overlap window, and the highest-severity interaction.\n"
                        "If no interactions are found, returns a one-line reassurance message. "
                        "This output is for benchmarking/simulation only, not clinical decision-making."
                    ),
                    "examples": [
                        # Example with multiple interactions (Sertraline + Warfarin, Aspirin)
                        (
                            "Drug interaction analysis:\n"
                            "Sertraline + Warfarin: severity=high, risk_score=9, overlap_hours=36. "
                            "Hold the next warfarin dose, monitor INR, and seek urgent clinical guidance.\n"
                            "Sertraline + Aspirin: severity=moderate, risk_score=6, overlap_hours=24. "
                            "Hold aspirin for 24 hours and observe for bleeding.\n"
                            "\n"
                            "Medications to hold today: Aspirin, Warfarin\n"
                            "Emergency escalation required: Yes\n"
                            "Peak overlap risk window (hours): 36\n"
                            "Highest severity interaction: Sertraline + Warfarin (high)"
                        ),
                        # Example with a single low-severity interaction
                        (
                            "Drug interaction analysis:\n"
                            "Sertraline + Metoprolol: severity=low, risk_score=3, overlap_hours=12. "
                            "Monitor for bradycardia; no dose adjustment typically needed.\n"
                            "\n"
                            "Medications to hold today: None\n"
                            "Emergency escalation required: No\n"
                            "Peak overlap risk window (hours): 12\n"
                            "Highest severity interaction: Sertraline + Metoprolol (low)"
                        ),
                        # Example when no interactions are found
                        (
                            "No documented high-risk interactions found for the supplied medications. "
                            "Continue monitoring as per care plan."
                        ),
                    ],
                },
            },
        }