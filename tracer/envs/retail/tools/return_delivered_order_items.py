# Copyright Sierra

import json
from typing import Any, Dict, List

from tau_bench.envs.retail.tools.return_delivered_order_items import (
    ReturnDeliveredOrderItems as _ReturnDeliveredOrderItems,
)


class ReturnDeliveredOrderItems(_ReturnDeliveredOrderItems):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "return_delivered_order_items",
                "description": (
                    "Return some items of a delivered order. The order status will be changed to 'return requested'. "
                    "The agent needs to explain the return detail and ask for explicit user confirmation (yes/no) to proceed. "
                    "The user will receive follow-up email for how and where to return the item. "
                    "Only orders with status 'delivered' can be returned."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": (
                                "The order id, such as '#W2611340'. Be careful there is a '#' symbol at the beginning of the order id."
                            ),
                        },
                        "item_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "The item ids to be returned, each such as '6469567736'. "
                                "There could be duplicate items in the list if multiple quantities of the same item are being returned."
                            ),
                        },
                        "payment_method_id": {
                            "type": "string",
                            "description": (
                                "The payment method id that should receive the refund, such as 'gift_card_0000000' or 'credit_card_0000000'. "
                                "It must be either the original payment method used for the order or a gift card stored in the user's profile."
                            ),
                        },
                    },
                    "required": ["order_id", "item_ids", "payment_method_id"],
                },
                "response": {
                    "type": "object",
                    "description": (
                        "The updated order object after marking items for return. "
                        "On success, the order status will be 'return requested' and the fields "
                        "'return_items' and 'return_payment_method_id' will be added. "
                        "If the order or payment method is invalid, or the order is not 'delivered', "
                        "the function instead returns an error string such as "
                        "'Error: order not found', 'Error: non-delivered order cannot be returned', "
                        "'Error: payment method not found', "
                        "'Error: payment method should be either the original payment method or a gift card', "
                        "or 'Error: some item not found'."
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
                                        "description": (
                                            "Item options such as size, color, material, etc."
                                        ),
                                        "additionalProperties": {"type": "string"},
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
                            "description": (
                                "Fulfillment information including tracking and which "
                                "items were shipped."
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "tracking_id": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of tracking IDs for this fulfillment.",
                                    },
                                    "item_ids": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of item IDs in this fulfillment.",
                                    },
                                },
                                "required": ["tracking_id", "item_ids"],
                            },
                        },
                        "status": {
                            "type": "string",
                            "description": (
                                "The current status of the order, e.g. 'delivered', 'return requested', etc."
                            ),
                        },
                        "payment_history": {
                            "type": "array",
                            "description": (
                                "History of payment-related transactions for the order. "
                                "For this function, it is not modified, but is returned as-is."
                            ),
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
                                        "description": "Identifier of the payment method used.",
                                    },
                                },
                                "required": [
                                    "transaction_type",
                                    "amount",
                                    "payment_method_id",
                                ],
                            },
                        },
                        "return_items": {
                            "type": "array",
                            "description": (
                                "Sorted list of item ids that the user has requested to return."
                            ),
                            "items": {"type": "string"},
                        },
                        "return_payment_method_id": {
                            "type": "string",
                            "description": (
                                "Payment method id that should receive the refund for the returned items."
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
                        "return_items",
                        "return_payment_method_id",
                    ],
                    "examples": [
                        {
                            "order_id": "#W2611340",
                            "user_id": "james_li_5688",
                            "address": {
                                "address1": "215 River Road",
                                "address2": "Suite 991",
                                "city": "New York",
                                "country": "USA",
                                "state": "NY",
                                "zip": "10083",
                            },
                            "items": [
                                {
                                    "name": "Water Bottle",
                                    "product_id": "8310926033",
                                    "item_id": "6469567736",
                                    "price": 47.84,
                                    "options": {
                                        "capacity": "1000ml",
                                        "material": "glass",
                                        "color": "blue",
                                    },
                                },
                                {
                                    "name": "Office Chair",
                                    "product_id": "4794339885",
                                    "item_id": "8426249116",
                                    "price": 488.81,
                                    "options": {
                                        "material": "fabric",
                                        "color": "black",
                                        "armrest": "fixed",
                                        "backrest height": "standard",
                                    },
                                },
                            ],
                            "fulfillments": [
                                {
                                    "tracking_id": ["357962501027"],
                                    "item_ids": ["6469567736", "8426249116"],
                                }
                            ],
                            "status": "return requested",
                            "payment_history": [
                                {
                                    "transaction_type": "payment",
                                    "amount": 536.65,
                                    "payment_method_id": "gift_card_1725971",
                                }
                            ],
                            "return_items": ["6469567736"],
                            "return_payment_method_id": "gift_card_1725971",
                        },
                        "Error: order not found",
                        "Error: non-delivered order cannot be returned",
                        "Error: payment method not found",
                        "Error: payment method should be either the original payment method or a gift card",
                        "Error: some item not found",
                    ],
                },
            },
        }