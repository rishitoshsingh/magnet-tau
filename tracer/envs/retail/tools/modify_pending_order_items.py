from typing import Any, Dict, List

from tau_bench.envs.retail.tools.modify_pending_order_items import (
    ModifyPendingOrderItems as _ModifyPendingOrderItems,
)


class ModifyPendingOrderItems(_ModifyPendingOrderItems):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_pending_order_items",
                "description": (
                    "Modify items in a pending order to new items of the same product type. "
                    "For a pending order, this function can only be called once. The agent "
                    "needs to explain the modification details and ask for explicit user "
                    "confirmation (yes/no) to proceed."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": (
                                "The order id, such as '#W5918442'. Be careful there is a "
                                "'#' symbol at the beginning of the order id."
                            ),
                        },
                        "item_ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                            "description": (
                                "The item ids to be modified, each such as '1725100896'. "
                                "There can be duplicate item ids in the list."
                            ),
                        },
                        "new_item_ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                            "description": (
                                "The new item ids to replace the original ones, each such as "
                                "'1586641416'. There can be duplicates. Each new item id must "
                                "correspond to the same product as the old item in the same position."
                            ),
                        },
                        "payment_method_id": {
                            "type": "string",
                            "description": (
                                "The payment method id to pay or receive refund for the item price "
                                "difference, such as 'gift_card_0000000' or 'credit_card_0000000'. "
                                "These can be looked up from the user or order details."
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
                        "The updated order object after modifying items. The items list, payment "
                        "history, and status may change. If the order does not exist, is not "
                        "pending, items are invalid, or payment fails, the function instead returns "
                        "an error string such as 'Error: order not found', "
                        "'Error: non-pending order cannot be modified', or "
                        "'Error: insufficient gift card balance to pay for the new item'."
                    ),
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "The unique ID of the order, such as '#W5918442'.",
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
                            "description": (
                                "List of items included in the order after modification. "
                                "Some item_ids, prices, and options may have changed."
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "Display name of the item, such as 'Action Camera'.",
                                    },
                                    "product_id": {
                                        "type": "string",
                                        "description": "Product identifier associated with the item.",
                                    },
                                    "item_id": {
                                        "type": "string",
                                        "description": "Line-item identifier within the order (variant id).",
                                    },
                                    "price": {
                                        "type": "number",
                                        "description": "Price of this item after modification.",
                                    },
                                    "options": {
                                        "type": "object",
                                        "description": "Item options such as color, size, material, etc.",
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
                                "Fulfillment information, including tracking and which items are "
                                "covered. For pending orders this is usually an empty list."
                            ),
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
                                "The current status of the order. After a successful modification "
                                "this will be 'pending (item modified)'."
                            ),
                        },
                        "payment_history": {
                            "type": "array",
                            "description": (
                                "History of payment-related transactions for the order, including "
                                "the original payment and any additional payment or refund created "
                                "by this modification."
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
                    "examples": [
                        {
                            "order_id": "#W5918442",
                            "user_id": "sofia_rossi_8776",
                            "address": {
                                "address1": "291 River Road",
                                "address2": "Suite 271",
                                "city": "Austin",
                                "country": "USA",
                                "state": "TX",
                                "zip": "78784",
                            },
                            "items": [
                                {
                                    "name": "Perfume",
                                    "product_id": "6858788497",
                                    "item_id": "1725100896",
                                    "price": 289.66,
                                    "options": {
                                        "scent family": "oriental",
                                        "size": "30ml",
                                        "gender": "unisex",
                                    },
                                },
                                {
                                    "name": "Skateboard",
                                    "product_id": "1968349452",
                                    "item_id": "5312063289",
                                    "price": 195.15,
                                    "options": {
                                        "deck material": "bamboo",
                                        "length": "31 inch",
                                        "design": "graphic",
                                    },
                                },
                                {
                                    "name": "Action Camera",
                                    "product_id": "3377618313",
                                    "item_id": "1586641416",
                                    "price": 497.39,
                                    "options": {
                                        "resolution": "5K",
                                        "waterproof": "yes",
                                        "color": "silver",
                                    },
                                },
                                {
                                    "name": "Action Camera",
                                    "product_id": "3377618313",
                                    "item_id": "6117189161",
                                    "price": 481.5,
                                    "options": {
                                        "resolution": "4K",
                                        "waterproof": "yes",
                                        "color": "silver",
                                    },
                                },
                            ],
                            "fulfillments": [],
                            "status": "pending (item modified)",
                            "payment_history": [
                                {
                                    "transaction_type": "payment",
                                    "amount": 1463.7,
                                    "payment_method_id": "credit_card_5051208",
                                },
                                {
                                    "transaction_type": "payment",
                                    "amount": 10.0,
                                    "payment_method_id": "gift_card_1234567",
                                },
                            ],
                        },
                        "Error: order not found",
                        "Error: non-pending order cannot be modified",
                        "Error: payment method not found",
                        "Error: insufficient gift card balance to pay for the new item",
                    ],
                },
            },
        }