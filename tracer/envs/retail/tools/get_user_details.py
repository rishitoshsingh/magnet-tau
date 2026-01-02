from typing import Any, Dict

from tau_bench.envs.retail.tools.get_user_details import (
    GetUserDetails as _GetUserDetails,
)


class GetUserDetails(_GetUserDetails):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_user_details",
                "description": "Get the details of a user, including their orders.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The user id, such as 'noah_brown_6181'.",
                        },
                    },
                    "required": ["user_id"],
                },
                "response": {
                    "type": "object",
                    "description": (
                        "The user profile object for the given user_id, including name, address, "
                        "email, payment methods, and order ids. If the user id does not exist, "
                        "the tool instead returns the string 'Error: user not found'."
                    ),
                    "properties": {
                        "name": {
                            "type": "object",
                            "description": "The user's name.",
                            "properties": {
                                "first_name": {
                                    "type": "string",
                                    "description": "The user's first name, such as 'Noah'.",
                                },
                                "last_name": {
                                    "type": "string",
                                    "description": "The user's last name, such as 'Brown'.",
                                },
                            },
                            "required": ["first_name", "last_name"],
                        },
                        "address": {
                            "type": "object",
                            "description": "The user's default shipping/billing address.",
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
                            "description": "The user's email address, such as 'noah.brown7922@example.com'.",
                        },
                        "payment_methods": {
                            "type": "object",
                            "description": (
                                "Mapping from payment method id to its details. Each entry contains at "
                                "least 'source' and 'id', and may contain additional fields like "
                                "'brand', 'last_four', or 'balance'."
                            ),
                            "additionalProperties": {
                                "type": "object",
                                "properties": {
                                    "source": {
                                        "type": "string",
                                        "description": "The type of payment method, such as 'paypal', 'credit_card', or 'gift_card'.",
                                    },
                                    "id": {
                                        "type": "string",
                                        "description": "The internal id of the payment method, such as 'credit_card_7815826'.",
                                    },
                                    "brand": {
                                        "type": "string",
                                        "description": "For card sources, the card brand, such as 'visa' or 'mastercard'.",
                                    },
                                    "last_four": {
                                        "type": "string",
                                        "description": "For card sources, the last four digits of the card number.",
                                    },
                                    "balance": {
                                        "type": "number",
                                        "description": "For gift cards, the remaining balance.",
                                    },
                                },
                                "required": ["source", "id"],
                            },
                        },
                        "orders": {
                            "type": "array",
                            "description": "List of order ids associated with this user.",
                            "items": {
                                "type": "string",
                                "description": "An order id, such as '#W7678072'.",
                            },
                        },
                    },
                    "required": ["name", "address", "email", "payment_methods", "orders"],
                    "examples": [
                        {
                            "name": {"first_name": "Noah", "last_name": "Brown"},
                            "address": {
                                "address1": "986 Sunset Drive",
                                "address2": "Suite 259",
                                "city": "Denver",
                                "country": "USA",
                                "state": "CO",
                                "zip": "80279",
                            },
                            "email": "noah.brown7922@example.com",
                            "payment_methods": {
                                "paypal_5727330": {
                                    "source": "paypal",
                                    "id": "paypal_5727330",
                                },
                                "credit_card_7815826": {
                                    "source": "credit_card",
                                    "brand": "mastercard",
                                    "last_four": "9212",
                                    "id": "credit_card_7815826",
                                },
                            },
                            "orders": ["#W7678072"],
                        },
                        "Error: user not found",
                    ],
                },
            },
        }