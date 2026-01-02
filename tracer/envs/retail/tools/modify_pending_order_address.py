from typing import Any, Dict

from tau_bench.envs.retail.tools.modify_pending_order_address import (
    ModifyPendingOrderAddress as _ModifyPendingOrderAddress,
)


class ModifyPendingOrderAddress(_ModifyPendingOrderAddress):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_pending_order_address",
                "description": (
                    "Modify the shipping address of a pending order. The agent must explain "
                    "the modification details and ask for explicit user confirmation (yes/no) "
                    "before proceeding. Only orders with status 'pending' may be modified."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "The order id, such as '#W5918442'.",
                        },
                        "address1": {
                            "type": "string",
                            "description": "The first line of the new address, such as '123 Main St'.",
                        },
                        "address2": {
                            "type": "string",
                            "description": "The second line of the address, such as 'Apt 1' or ''.",
                        },
                        "city": {
                            "type": "string",
                            "description": "The city name, such as 'Austin'.",
                        },
                        "state": {
                            "type": "string",
                            "description": "The state code, such as 'TX'.",
                        },
                        "country": {
                            "type": "string",
                            "description": "The country name, such as 'USA'.",
                        },
                        "zip": {
                            "type": "string",
                            "description": "The zip code, such as '78784'.",
                        },
                    },
                    "required": [
                        "order_id",
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
                        "The updated order object after the address has been modified. "
                        "If the order does not exist or is not pending, the function instead "
                        "returns a string error message such as 'Error: order not found' "
                        "or 'Error: non-pending order cannot be modified'."
                    ),
                    "properties": {
                        "order_id": {"type": "string"},
                        "user_id": {"type": "string"},
                        "address": {
                            "type": "object",
                            "properties": {
                                "address1": {"type": "string"},
                                "address2": {"type": "string"},
                                "city": {"type": "string"},
                                "state": {"type": "string"},
                                "country": {"type": "string"},
                                "zip": {"type": "string"},
                            },
                            "required": [
                                "address1", "address2", "city", "state", "country", "zip"
                            ],
                        },
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "product_id": {"type": "string"},
                                    "item_id": {"type": "string"},
                                    "price": {"type": "number"},
                                    "options": {
                                        "type": "object",
                                        "additionalProperties": {"type": "string"}
                                    },
                                },
                                "required": ["name", "product_id", "item_id", "price"],
                            },
                        },
                        "fulfillments": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "tracking_id": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "item_ids": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                },
                                "required": ["tracking_id", "item_ids"],
                            },
                        },
                        "status": {"type": "string"},
                        "payment_history": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "transaction_type": {"type": "string"},
                                    "amount": {"type": "number"},
                                    "payment_method_id": {"type": "string"},
                                },
                                "required": [
                                    "transaction_type", "amount", "payment_method_id"
                                ],
                            },
                        },
                    },
                    "required": [
                        "order_id",
                        "user_id",
                        "address",
                        "items",
                        "fulfillments",
                        "status",
                        "payment_history",
                    ],
                },
            },
        }