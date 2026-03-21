from typing import Any, Dict

from tau_bench.envs.telecom.tools.create_support_ticket import (
    CreateSupportTicket as _CreateSupportTicket,
)


class CreateSupportTicket(_CreateSupportTicket):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_support_ticket",
                "description": (
                    "Create a new support ticket for a customer. Validates the customer_id, "
                    "ticket category, and priority. On success, a ticket ID is generated and "
                    "the ticket is stored with status 'open'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": (
                                "The customer's unique identifier, such as 'john_smith_1234'. "
                                "Must exist in the system."
                            ),
                        },
                        "category": {
                            "type": "string",
                            "enum": ["mobile", "internet", "tv", "billing", "account", "device", "security", "phone"],
                            "description": (
                                "Ticket category. Must be one of: mobile, internet, tv, billing, "
                                "account, device, security, or phone."
                            ),
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": (
                                "Priority level. Defaults to 'medium'. "
                                "low = non-urgent, medium = standard, high = important, urgent = critical."
                            ),
                        },
                    },
                    "required": ["customer_id", "category"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "Returns a success message such as "
                        "'Success: Created support ticket TICKET001 for customer john_smith_1234' "
                        "or an error message starting with 'Error:' if validation fails."
                    ),
                    "examples": [
                        # Success
                        "Success: Created support ticket TICKET001 for customer john_smith_1234",

                        # Customer not found
                        "Error: Customer not found: unknown_cust_9999",

                        # Invalid category
                        "Error: Invalid category: plumbing. Valid categories: mobile, internet, tv, billing, account, device, security, phone",

                        # Invalid priority
                        "Error: Invalid priority: extreme. Valid priorities: low, medium, high, urgent"
                    ],
                },
            },
        }