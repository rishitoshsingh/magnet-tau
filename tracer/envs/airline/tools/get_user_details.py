from typing import Any, Dict

from tau_bench.envs.airline.tools.get_user_details import (
    GetUserDetails as _GetUserDetails,
)


class GetUserDetails(_GetUserDetails):

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_user_details",
                "description": "Get the details of a user, including their profile, payment methods, saved passengers, and reservations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The user id, such as 'mia_li_3668'.",
                        },
                    },
                    "required": ["user_id"],
                },
                "response": {
                    "type": "object",
                    "description": "The complete user record as stored in the system.",
                    "properties": {
                        "name": {
                            "type": "object",
                            "properties": {
                                "first_name": {"type": "string"},
                                "last_name": {"type": "string"},
                            },
                            "required": ["first_name", "last_name"],
                        },
                        "address": {
                            "type": "object",
                            "properties": {
                                "address1": {"type": "string"},
                                "address2": {"type": "string"},
                                "city": {"type": "string"},
                                "country": {"type": "string"},
                                "state": {"type": "string"},
                                "zip": {"type": "string"},
                            },
                            "required": [
                                "address1",
                                "city",
                                "country",
                                "state",
                                "zip",
                            ],
                        },
                        "email": {
                            "type": "string",
                            "description": "The user's email address.",
                        },
                        "dob": {
                            "type": "string",
                            "description": "Date of birth in 'YYYY-MM-DD' format.",
                        },
                        "payment_methods": {
                            "type": "object",
                            "description": "Mapping from payment ID to its details.",
                            "additionalProperties": {
                                "type": "object",
                                "properties": {
                                    "source": {
                                        "type": "string",
                                        "enum": ["credit_card", "gift_card", "certificate"],
                                    },
                                    "brand": {
                                        "type": "string",
                                        "description": "Brand for credit cards (e.g., visa, mastercard).",
                                    },
                                    "last_four": {
                                        "type": "string",
                                        "description": "Last four digits of a credit card.",
                                    },
                                    "amount": {
                                        "type": "number",
                                        "description": "Remaining balance for certificates or gift cards.",
                                    },
                                    "id": {
                                        "type": "string",
                                        "description": "The payment method ID.",
                                    },
                                },
                                "required": ["source", "id"],
                            },
                        },
                        "saved_passengers": {
                            "type": "array",
                            "description": "Saved passenger profiles.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "first_name": {"type": "string"},
                                    "last_name": {"type": "string"},
                                    "dob": {
                                        "type": "string",
                                        "description": "Date of birth in 'YYYY-MM-DD'.",
                                    },
                                },
                                "required": ["first_name", "last_name", "dob"],
                            },
                        },
                        "membership": {
                            "type": "string",
                            "description": "User's loyalty tier, such as 'silver', 'gold', 'platinum'.",
                        },
                        "reservations": {
                            "type": "array",
                            "description": "List of reservation IDs owned by the user.",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "name",
                        "address",
                        "email",
                        "dob",
                        "payment_methods",
                        "saved_passengers",
                        "membership",
                        "reservations",
                    ],
                },
            },
        }