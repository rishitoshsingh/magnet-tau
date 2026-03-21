
from typing import Any, Dict

from tau_bench.envs.telehealth.tools.get_provider_details import (
    GetProviderDetails as _GetProviderDetails,
)


class GetProviderDetails(_GetProviderDetails):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_provider_details",
                "description": (
                    "Get detailed information about a healthcare provider including specialty, license, "
                    "credentials, languages, consultation fee, contact information, and weekly schedule. "
                    "Returns a formatted multi-line string, or an error message if the provider is not found."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "provider_id": {
                            "type": "string",
                            "description": (
                                "The provider's unique identifier, such as 'dr_smith_cardiology' "
                                "or 'dr_thompson_cardiology'."
                            ),
                        },
                    },
                    "required": ["provider_id"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "Human-readable multi-line provider summary, or an error message. "
                        "Includes:\n"
                        "- Name and ID\n"
                        "- Specialty\n"
                        "- License number\n"
                        "- Credentials and years of experience\n"
                        "- Contact information (phone, email)\n"
                        "- Languages\n"
                        "- Consultation fee\n"
                        "- Weekly schedule by weekday and available times"
                    ),
                    "examples": [
                        (
                            "Provider Details (ID: dr_smith_cardiology)\n\n"
                            "Name: MD Robert Smith\n"
                            "Specialty: Cardiology\n"
                            "License Number: MD12345\n"
                            "Credentials: MD, FACC\n"
                            "Years of Experience: 15\n\n"
                            "Contact Information:\n"
                            "- Phone: (555) 100-2001\n"
                            "- Email: dr.smith@healthcenter.com\n\n"
                            "Languages: English, Spanish\n"
                            "Consultation Fee: $200.00\n\n"
                            "Weekly Schedule:\n"
                            "- Monday: 09:00, 10:00, 11:00, 15:00, 16:00\n"
                            "- Tuesday: 09:00, 10:00, 11:00, 15:00\n"
                            "- Wednesday: 09:00, 10:00, 15:00, 16:00\n"
                            "- Thursday: 09:00, 10:00, 11:00, 15:00, 16:00\n"
                            "- Friday: 09:00, 10:00, 11:00, 15:00"
                        ),
                        (
                            "Provider Details (ID: dr_thompson_cardiology)\n\n"
                            "Name: MD Margaret Thompson\n"
                            "Specialty: Cardiology\n"
                            "License Number: MD67890\n"
                            "Credentials: MD, FACC, FSCAI\n"
                            "Years of Experience: 25\n\n"
                            "Contact Information:\n"
                            "- Phone: (555) 100-2005\n"
                            "- Email: dr.thompson@healthcenter.com\n\n"
                            "Languages: English\n"
                            "Consultation Fee: $275.00\n\n"
                            "Weekly Schedule:\n"
                            "- Monday: 08:00, 09:00, 10:00, 11:00, 14:00, 15:00\n"
                            "- Tuesday: 08:00, 09:00, 10:00, 11:00, 14:00\n"
                            "- Wednesday: 08:00, 09:00, 10:00, 14:00, 15:00\n"
                            "- Thursday: 08:00, 09:00, 10:00, 11:00, 14:00, 15:00\n"
                            "- Friday: 08:00, 09:00, 10:00, 11:00"
                        ),
                        # Error case:
                        "Provider with ID dr_unknown_9999 not found."
                    ],
                },
            },
        }