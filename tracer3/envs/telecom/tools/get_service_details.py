from typing import Any, Dict

from tau_bench.envs.telecom.tools.get_service_details import (
    GetServiceDetails as _GetServiceDetails,
)


class GetServiceDetails(_GetServiceDetails):

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_service_details",
                "description": (
                    "Get detailed information about a telecom service. "
                    "Returns service metadata including name, category, and price. "
                    "If the service_id is not found, an error string is returned."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "description": (
                                "The service identifier, such as 'mobile_unlimited', "
                                "'internet_fiber_1gb', or 'tv_premium'."
                            ),
                        },
                    },
                    "required": ["service_id"],
                },
                "response": {
                    "type": "object",
                    "description": (
                        "The service details object, including service_id, name, category, and price. "
                        "If the service is not found, the function returns the string "
                        "'Error: Service not found: <service_id>'."
                    ),
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
                            "description": "Service category, such as 'mobile', 'internet', or 'tv'."
                        },
                        "price": {
                            "type": "number",
                            "description": "Monthly price of the service."
                        },
                    },
                    "required": ["service_id", "name", "category", "price"],
                    "examples": [
                        {
                            "service_id": "mobile_unlimited",
                            "name": "Unlimited Mobile Plan",
                            "category": "mobile",
                            "price": 85.00
                        },
                        {
                            "service_id": "mobile_business_10lines",
                            "name": "Business Mobile - 10 Lines",
                            "category": "mobile",
                            "price": 450.00
                        },
                        "Error: Service not found: mobile_prepaid_500mb"
                    ],
                },
            },
        }