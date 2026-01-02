
from typing import Any, Dict

from tau_bench.envs.telehealth.tools.list_available_providers import (
    ListAvailableProviders as _ListAvailableProviders,
)


class ListAvailableProviders(_ListAvailableProviders):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_available_providers",
                "description": (
                    "List all available healthcare providers, optionally filtered by specialty. "
                    "If a specialty is provided, only providers whose specialty matches (case-insensitive) "
                    "will be returned. Output is a human-readable multi-line summary."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "specialty": {
                            "type": "string",
                            "description": (
                                "Optional specialty name to filter providers by, such as "
                                "'Cardiology', 'Primary Care', 'Psychiatry', 'Dermatology'."
                            ),
                        },
                    },
                    "required": [],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "Returns a formatted list of providers matching the specialty filter (if given). "
                        "Each provider includes name, ID, specialty, years of experience, languages, "
                        "consultation fee, and phone. "
                        "Returns an error-like string if no providers match the query."
                    ),
                    "examples": [
                        # SUCCESS — all providers
                        (
                            "Available Providers:\n\n"
                            "• MD Robert Smith (ID: dr_smith_cardiology)\n"
                            "  Specialty: Cardiology\n"
                            "  Experience: 15 years\n"
                            "  Languages: English, Spanish\n"
                            "  Consultation Fee: $200.00\n"
                            "  Phone: (555) 100-2001"
                        ),

                        # SUCCESS — filtered list
                        (
                            "Available Providers - Cardiology:\n\n"
                            "• MD Robert Smith (ID: dr_smith_cardiology)\n"
                            "  Specialty: Cardiology\n"
                            "  Experience: 15 years\n"
                            "  Languages: English, Spanish\n"
                            "  Consultation Fee: $200.00\n"
                            "  Phone: (555) 100-2001"
                        ),

                        # NO MATCH
                        "No providers found with specialty: Dermatology",

                        # NO PROVIDERS AT ALL (edge case)
                        "No providers found."
                    ],
                },
            },
        }