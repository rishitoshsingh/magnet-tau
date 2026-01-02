from typing import Any, Dict

from tau_bench.envs.telecom.tools.get_senior_discount import (
    GetSeniorDiscount as _GetSeniorDiscount,
)


class GetSeniorDiscount(_GetSeniorDiscount):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_senior_discount",
                "description": (
                    "Apply a fixed $5 senior discount to the provided service price. "
                    "If the discount results in a negative value, the final price is returned as 0.00. "
                    "If the input is not a valid number, an error string is returned."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "original_price": {
                            "type": "string",
                            "description": (
                                "Original price before applying the senior discount. "
                                "Must be convertible to a number. Example: '95.00'."
                            ),
                        },
                    },
                    "required": ["original_price"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "Returns the discounted price as a string formatted to two decimal places, "
                        "or an error string if the input is not a valid number."
                    ),
                    "examples": [
                        # Successful cases
                        "90.00",   # 95.00 - 5.00
                        "0.00",    # discount cannot go below zero
                        # Error cases
                        "Error: original_price must be a number"
                    ],
                },
            },
        }