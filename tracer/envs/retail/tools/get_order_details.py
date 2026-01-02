from typing import Any, Dict

from tau_bench.envs.retail.tools.get_order_details import (
    GetOrderDetails as _GetOrderDetails,
)


class GetOrderDetails(_GetOrderDetails):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_order_details",
                "description": "Get the status and details of an order.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": (
                                "The order id, such as '#W0000000'. Be careful there is a '#' symbol "
                                "at the beginning of the order id."
                            ),
                        },
                    },
                    "required": ["order_id"],
                },
                "response": {
                    "type": "object",
                    "description": (
                        "The full order record if found. Includes address, items, fulfillments, "
                        "status, and payment history."
                    ),
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "The unique ID of the order, such as '#W2611340'.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user who placed the order.",
                        },
                        "address": {
                            "type": "object",
                            "description": "Shipping address for the order.",
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
                        "items": {
                            "type": "array",
                            "description": "List of items included in the order.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "Display name of the item, such as 'Water Bottle'.",
                                    },
                                    "product_id": {
                                        "type": "string",
                                        "description": "Product identifier.",
                                    },
                                    "item_id": {
                                        "type": "string",
                                        "description": "Line-item identifier within the order.",
                                    },
                                    "price": {
                                        "type": "number",
                                        "description": "Price of the item.",
                                    },
                                    "options": {
                                        "type": "object",
                                        "description": "Item options such as size, color, material, etc.",
                                        "additionalProperties": {
                                            "type": "string",
                                        },
                                    },
                                },
                                "required": [
                                    "name",
                                    "product_id",
                                    "item_id",
                                    "price",
                                ],
                            },
                        },
                        "fulfillments": {
                            "type": "array",
                            "description": "Fulfillment information including tracking and which items were shipped.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "tracking_id": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of tracking IDs associated with this fulfillment.",
                                    },
                                    "item_ids": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of item IDs included in this fulfillment.",
                                    },
                                },
                                "required": ["tracking_id", "item_ids"],
                            },
                        },
                        "status": {
                            "type": "string",
                            "description": (
                                "The current status of the order, such as 'pending', "
                                "'processed', 'delivered', or 'cancelled'."
                            ),
                        },
                        "payment_history": {
                            "type": "array",
                            "description": "History of payment-related transactions for the order.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "transaction_type": {
                                        "type": "string",
                                        "description": "Type of transaction, e.g., 'payment' or 'refund'.",
                                    },
                                    "amount": {
                                        "type": "number",
                                        "description": "Amount of the transaction.",
                                    },
                                    "payment_method_id": {
                                        "type": "string",
                                        "description": "Identifier of the payment method used for this transaction.",
                                    },
                                },
                                "required": [
                                    "transaction_type",
                                    "amount",
                                    "payment_method_id",
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