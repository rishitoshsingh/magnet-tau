from typing import Any, Dict

from tau_bench.envs.retail.tools.list_all_product_types import (
    ListAllProductTypes as _ListAllProductTypes,
)


class ListAllProductTypes(_ListAllProductTypes):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_all_product_types",
                "description": (
                    "List the name and product id of all product types. "
                    "Each product type has a variety of different items with unique item ids and options. "
                    "There are only 50 product types in the store."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
                "response": {
                    "type": "object",
                    "description": (
                        "A mapping from product name to product_id for all product types in the catalog. "
                        "Keys are human-readable product names (e.g. 'T-Shirt'), and values are product "
                        "IDs (e.g. '9523456873')."
                    ),
                    "additionalProperties": {
                        "type": "string",
                        "description": "The product_id corresponding to the product name key.",
                    },
                    "examples": [
                        {
                            "T-Shirt": "9523456873",
                            "Laptop": "4760268021",
                            "Running Shoes": "6938111410"
                            # ... up to all ~50 product types
                        }
                    ],
                },
            },
        }