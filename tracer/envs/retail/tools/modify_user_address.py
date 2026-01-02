from typing import Any, Dict

from tau_bench.envs.retail.tools.modify_user_address import (
    ModifyUserAddress as _ModifyUserAddress,
)


class ModifyUserAddress(_ModifyUserAddress):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_user_address",
                "description": (
                    "Modify the default address of a user. The agent must explain what will be changed "
                    "and ask for explicit user confirmation (yes/no) before calling this function. "
                    "On success, it returns the full updated user profile; on failure, it returns an "
                    "error string such as 'Error: user not found'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The user id, such as 'noah_brown_6181' or 'ivan_santos_6635'.",
                        },
                        "address1": {
                            "type": "string",
                            "description": "The first line of the address, such as '123 Main St'.",
                        },
                        "address2": {
                            "type": "string",
                            "description": "The second line of the address, such as 'Apt 1' or ''.",
                        },
                        "city": {
                            "type": "string",
                            "description": "The city, such as 'San Francisco'.",
                        },
                        "state": {
                            "type": "string",
                            "description": "The state, such as 'CA'.",
                        },
                        "country": {
                            "type": "string",
                            "description": "The country, such as 'USA'.",
                        },
                        "zip": {
                            "type": "string",
                            "description": "The zip code, such as '12345'.",
                        },
                    },
                    "required": [
                        "user_id",
                        "address1",
                        "address2",
                        "city",
                        "state",
                        "country",
                        "zip",
                    ],
                },
                "response": {
                    "type": "object",
                    "description": (
                        "The updated user profile after modifying the default address. "
                        "If the user id does not exist, the function instead returns the string "
                        "'Error: user not found'."
                    ),
                    "properties": {
                        "name": {
                            "type": "object",
                            "description": "User's name.",
                            "properties": {
                                "first_name": {
                                    "type": "string",
                                    "description": "First name of the user.",
                                },
                                "last_name": {
                                    "type": "string",
                                    "description": "Last name of the user.",
                                },
                            },
                            "required": ["first_name", "last_name"],
                        },
                        "address": {
                            "type": "object",
                            "description": "User's default shipping address after the update.",
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
                        "payment_methods": {
                            "type": "object",
                            "description": "Stored payment methods keyed by payment method id.",
                            "additionalProperties": {
                                "type": "object",
                                "properties": {
                                    "source": {
                                        "type": "string",
                                        "description": "Type of payment method, e.g. 'paypal', 'credit_card', 'gift_card'.",
                                    },
                                    "id": {
                                        "type": "string",
                                        "description": "Payment method id, such as 'credit_card_7815826'.",
                                    },
                                    "brand": {
                                        "type": "string",
                                        "description": "Card brand for credit cards, such as 'visa' or 'mastercard'.",
                                    },
                                    "last_four": {
                                        "type": "string",
                                        "description": "Last four digits of the card number.",
                                    },
                                    "balance": {
                                        "type": "number",
                                        "description": "Remaining balance for gift cards, if applicable.",
                                    },
                                },
                                "required": ["source", "id"],
                            },
                        },
                        "orders": {
                            "type": "array",
                            "description": "List of order ids associated with the user.",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["name", "address", "email", "payment_methods", "orders"],
                    "examples": [
                        {
                            "name": {"first_name": "Noah", "last_name": "Brown"},
                            "address": {
                                "address1": "123 Main St",
                                "address2": "Apt 4B",
                                "city": "San Francisco",
                                "country": "USA",
                                "state": "CA",
                                "zip": "94105",
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
                        {
                            "name": {"first_name": "Ivan", "last_name": "Santos"},
                            "address": {
                                "address1": "100 New Street",
                                "address2": "Suite 100",
                                "city": "Austin",
                                "country": "USA",
                                "state": "TX",
                                "zip": "78701",
                            },
                            "email": "ivan.santos3158@example.com",
                            "payment_methods": {
                                "paypal_6151711": {
                                    "source": "paypal",
                                    "id": "paypal_6151711",
                                }
                            },
                            "orders": ["#W6893533", "#W8770097", "#W5183325", "#W3913498"],
                        },
                        "Error: user not found",
                    ],
                },
            },
        }