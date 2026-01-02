from typing import Any, Dict

from tau_bench.envs.retail.tools.get_product_details import (
    GetProductDetails as _GetProductDetails,
)


class GetProductDetails(_GetProductDetails):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_product_details",
                "description": "Get the inventory details (variants, availability, and pricing) of a product.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "string",
                            "description": (
                                "The product id, such as '9523456873'. "
                                "Be careful: product id is different from item id."
                            ),
                        },
                    },
                    "required": ["product_id"],
                },
                "response": {
                    "type": "object",
                    "description": (
                        "The full product record, including all variant item_ids, options, "
                        "availability, and pricing. Returns 'Error: product not found' if the "
                        "product_id does not exist."
                    ),
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Human-readable product name such as 'T-Shirt'.",
                        },
                        "product_id": {
                            "type": "string",
                            "description": "The product identifier, matching the input product_id.",
                        },
                        "variants": {
                            "type": "object",
                            "description": (
                                "A mapping of variant item_id → variant details. "
                                "Each variant represents a specific purchasable SKU."
                            ),
                            "additionalProperties": {
                                "type": "object",
                                "properties": {
                                    "item_id": {
                                        "type": "string",
                                        "description": "Unique ID of this purchasable item/SKU.",
                                    },
                                    "options": {
                                        "type": "object",
                                        "description": "Option attributes such as color, size, material, style, etc.",
                                        "additionalProperties": {"type": "string"},
                                    },
                                    "available": {
                                        "type": "boolean",
                                        "description": "Whether this specific variant is currently in stock.",
                                    },
                                    "price": {
                                        "type": "number",
                                        "description": "The price of this specific product variant.",
                                    },
                                },
                                "required": ["item_id", "options", "available", "price"],
                            },
                        },
                    },
                    "required": ["name", "product_id", "variants"],
                    "examples": [
                        {
                            "name": "T-Shirt",
                            "product_id": "9523456873",
                            "variants": {
                                "9612497925": {
                                    "item_id": "9612497925",
                                    "options": {
                                        "color": "blue",
                                        "size": "M",
                                        "material": "cotton",
                                        "style": "crew neck"
                                    },
                                    "available": True,
                                    "price": 50.88
                                }
                            }
                        },
                        "Error: product not found"
                    ]
                },
            },
        }