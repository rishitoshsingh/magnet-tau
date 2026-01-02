from typing import Any, Dict

from tau_bench.envs.telecom.tools.manage_service import ManageService as _ManageService


class ManageService(_ManageService):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "manage_service",
                "description": (
                    "Manage customer services: add, remove, or list services on an account. "
                    "For 'list', the function returns a JSON object of the customer's services. "
                    "For 'add' and 'remove', it returns a human-readable status string. "
                    "On failure (e.g., invalid customer, service, action, or device), it returns an error string."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": (
                                "The customer's unique identifier, such as 'john_smith_1234'."
                            ),
                        },
                        "action": {
                            "type": "string",
                            "enum": ["add", "remove", "list"],
                            "description": (
                                "Action to perform on the customer's services: "
                                "'list' to retrieve all services, "
                                "'add' to add a service, "
                                "'remove' to remove a service."
                            ),
                        },
                        "service_id": {
                            "type": "string",
                            "description": (
                                "The service identifier, such as 'mobile_unlimited'. "
                                "Required when action is 'add' or 'remove'. "
                                "Ignored for 'list'."
                            ),
                        },
                        "devices_ids": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": (
                                "Optional list of device IDs to associate with the service when action is 'add'. "
                                "Each ID must match a 'device_id' in the customer's devices list. "
                                "Ignored for 'list'. When removing a service, all devices currently "
                                "associated with that service are automatically detached."
                            ),
                        },
                    },
                    "required": ["customer_id", "action"],
                },
                "response": {
                    "anyOf": [
                        {
                            "type": "object",
                            "description": (
                                "Returned when action is 'list': the customer's current services enriched "
                                "with service details."
                            ),
                            "properties": {
                                "customer_id": {
                                    "type": "string",
                                    "description": "The customer's unique identifier.",
                                },
                                "services": {
                                    "type": "array",
                                    "description": (
                                        "List of service objects for this customer. Each entry comes from the "
                                        "global 'services' catalog."
                                    ),
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "service_id": {
                                                "type": "string",
                                                "description": "Service identifier, e.g. 'mobile_unlimited'.",
                                            },
                                            "name": {
                                                "type": "string",
                                                "description": "Human-readable service name.",
                                            },
                                            "category": {
                                                "type": "string",
                                                "description": "Service category, e.g. 'mobile', 'internet', 'tv'.",
                                            },
                                            "price": {
                                                "type": "number",
                                                "description": "Standard monthly price of the service.",
                                            },
                                        },
                                        "required": ["service_id", "name", "category", "price"],
                                    },
                                },
                            },
                            "required": ["customer_id", "services"],
                        },
                        {
                            "type": "string",
                            "description": (
                                "Status or error message returned when action is 'add' or 'remove', "
                                "or when an error occurs. For example:\n"
                                "- 'Success: Added service ...'\n"
                                "- 'Success: Removed service ...'\n"
                                "- 'Error: Customer not found: ...'\n"
                                "- 'Error: Service not found: ...'"
                            ),
                        },
                    ],
                    "examples": [
                        {
                            "customer_id": "john_smith_1234",
                            "services": [
                                {
                                    "service_id": "mobile_unlimited",
                                    "name": "Unlimited Mobile Plan",
                                    "category": "mobile",
                                    "price": 85.00,
                                },
                                {
                                    "service_id": "internet_fiber_1gb",
                                    "name": "Fiber Internet 1 Gbps",
                                    "category": "internet",
                                    "price": 80.00,
                                },
                                {
                                    "service_id": "tv_premium",
                                    "name": "Premium TV Package",
                                    "category": "tv",
                                    "price": 95.00,
                                },
                            ],
                        },
                        "Success: Added service 'Unlimited Mobile Plan' to customer john_smith_1234",
                        (
                            "Success: Removed service 'Unlimited Mobile Plan' from customer john_smith_1234. "
                            "Devices ['iPhone 15 Pro'] are now no longer associated with the service."
                        ),
                        "Error: Customer not found: unknown_customer",
                        "Error: Service not found: mobile_unlimited_plus",
                        "Error: Invalid action: update. Valid actions are: add, remove, list",
                    ],
                },
            },
        }