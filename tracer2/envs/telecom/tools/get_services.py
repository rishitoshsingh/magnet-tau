from typing import Any, Dict

from tau_bench.envs.telecom.tools.get_services import GetServices as _GetServices


class GetServices(_GetServices):

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_services",
                "description": (
                    "Get detailed information about all telecom services available in the catalog. "
                    "Returns a mapping from service_id to service details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
                "response": {
                    "type": "object",
                    "description": (
                        "A dictionary of all available telecom services. Each key is a service_id, "
                        "and each value is an object describing the service (service_id, name, category, price)."
                    ),
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "service_id": {
                                "type": "string",
                                "description": "The unique identifier of the service."
                            },
                            "name": {
                                "type": "string",
                                "description": "Human-readable service name."
                            },
                            "category": {
                                "type": "string",
                                "description": "Category of the service, e.g. 'mobile', 'internet', 'tv'."
                            },
                            "price": {
                                "type": "number",
                                "description": "Monthly service price."
                            },
                        },
                        "required": ["service_id", "name", "category", "price"],
                    },
                    "examples": [
                        {
                            "mobile_unlimited": {
                                "service_id": "mobile_unlimited",
                                "name": "Unlimited Mobile Plan",
                                "category": "mobile",
                                "price": 85.00
                            },
                            "mobile_family_4lines": {
                                "service_id": "mobile_family_4lines",
                                "name": "Family Plan - 4 Lines",
                                "category": "mobile",
                                "price": 160.00
                            },
                            "mobile_business_10lines": {
                                "service_id": "mobile_business_10lines",
                                "name": "Business Mobile - 10 Lines",
                                "category": "mobile",
                                "price": 450.00
                            }
                        }
                    ],
                },
            },
        }