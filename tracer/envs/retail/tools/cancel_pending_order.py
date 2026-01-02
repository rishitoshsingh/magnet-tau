from typing import Any, Dict

from tau_bench.envs.retail.tools.cancel_pending_order import (
    CancelPendingOrder as _CancelPendingOrder,
)


class CancelPendingOrder(_CancelPendingOrder):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "cancel_pending_order",
                "description": (
                    "Cancel a pending order. If the order is already processed or delivered, "
                    "it cannot be cancelled. The agent needs to explain the cancellation detail "
                    "and ask for explicit user confirmation (yes/no) to proceed. If the user confirms, "
                    "the order status will be changed to 'cancelled' and the payment will be refunded. "
                    "The refund will be added to the user's gift card balance immediately if the payment "
                    "was made using a gift card, otherwise the refund would take 5-7 business days to process. "
                    "The function returns the order details after the cancellation."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.",
                        },
                        "reason": {
                            "type": "string",
                            "enum": ["no longer needed", "ordered by mistake"],
                            "description": "The reason for cancellation, which should be either 'no longer needed' or 'ordered by mistake'.",
                        },
                    },
                    "required": ["order_id", "reason"],
                },
                "response": {
                    "type": "object",
                    "description": "The order record after a successful cancellation, including updated status, cancel reason, and appended refund entries in payment_history.",
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
                            "description": "The current status of the order. After successful cancellation this will be 'cancelled'.",
                        },
                        "cancel_reason": {
                            "type": "string",
                            "description": "The reason used for cancellation, such as 'no longer needed' or 'ordered by mistake'.",
                        },
                        "payment_history": {
                            "type": "array",
                            "description": (
                                "History of payment-related transactions for the order. "
                                "Includes original 'payment' entries and appended 'refund' entries after cancellation."
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
                                        "description": "Amount of the transaction. Refund amounts are positive here but semantically represent funds returned.",
                                    },
                                    "payment_method_id": {
                                        "type": "string",
                                        "description": "Identifier of the payment method used for this transaction (e.g., 'gift_card_1725971').",
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
                        "cancel_reason",
                    ],
                },
            },
        }