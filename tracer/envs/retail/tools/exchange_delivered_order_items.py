from typing import Any, Dict

from tau_bench.envs.retail.tools.exchange_delivered_order_items import (
    ExchangeDeliveredOrderItems as _ExchangeDeliveredOrderItems,
)


class ExchangeDeliveredOrderItems(_ExchangeDeliveredOrderItems):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "exchange_delivered_order_items",
                "description": (
                    "Exchange items in a delivered order to new items of the same product type. "
                    "For a delivered order, return or exchange can be only done once by the agent. "
                    "The agent needs to explain the exchange detail and ask for explicit user confirmation (yes/no) to proceed."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.",
                        },
                        "item_ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                            "description": "The item ids to be exchanged, each such as '1008292230'. There could be duplicate items in the list.",
                        },
                        "new_item_ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                            "description": (
                                "The item ids to be exchanged for, each such as '1008292230'. "
                                "There could be duplicate items in the list. Each new item id should match the item id in the same position and be of the same product."
                            ),
                        },
                        "payment_method_id": {
                            "type": "string",
                            "description": (
                                "The payment method id to pay or receive refund for the item price difference, "
                                "such as 'gift_card_0000000' or 'credit_card_0000000'. These can be looked up from the user or order details."
                            ),
                        },
                    },
                    "required": [
                        "order_id",
                        "item_ids",
                        "new_item_ids",
                        "payment_method_id",
                    ],
                },
                "response": {
                    "type": "object",
                    "description": (
                        "The updated order record after requesting an exchange. "
                        "Includes new status, exchange item mappings, and the price difference."
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
                                        "description": "Item options such as color, size, material, etc.",
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
                            "description": "Fulfillment information including shipping tracking and which items are covered.",
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
                                "The current status of the order. "
                                "After a successful exchange request this will be 'exchange requested'."
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
                        "exchange_items": {
                            "type": "array",
                            "description": (
                                "Sorted list of original item_ids that the user requested to exchange."
                            ),
                            "items": {"type": "string"},
                        },
                        "exchange_new_items": {
                            "type": "array",
                            "description": (
                                "Sorted list of new item_ids that will replace the original items."
                            ),
                            "items": {"type": "string"},
                        },
                        "exchange_payment_method_id": {
                            "type": "string",
                            "description": (
                                "The payment method ID that will be charged or refunded "
                                "for the price difference of the exchange."
                            ),
                        },
                        "exchange_price_difference": {
                            "type": "number",
                            "description": (
                                "Total price difference between new items and original items "
                                "for the exchange, rounded to two decimals. "
                                "Can be positive (user pays more), negative (user is refunded), or zero."
                            ),
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
                        "exchange_items",
                        "exchange_new_items",
                        "exchange_payment_method_id",
                        "exchange_price_difference",
                    ],
                },
            },
        }