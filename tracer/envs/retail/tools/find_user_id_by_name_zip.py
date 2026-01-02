from typing import Any, Dict

from tau_bench.envs.retail.tools.find_user_id_by_name_zip import (
    FindUserIdByNameZip as _FindUserIdByNameZip,
)


class FindUserIdByNameZip(_FindUserIdByNameZip):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "find_user_id_by_name_zip",
                "description": (
                    "Find user id by first name, last name, and zip code. If the user is not found, "
                    "the function returns an error message. This function should only be used when "
                    "the user cannot recall their email or was not found by email."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "first_name": {
                            "type": "string",
                            "description": "The first name of the customer, such as 'John'.",
                        },
                        "last_name": {
                            "type": "string",
                            "description": "The last name of the customer, such as 'Doe'.",
                        },
                        "zip": {
                            "type": "string",
                            "description": "The customer’s ZIP code, such as '80279'.",
                        },
                    },
                    "required": ["first_name", "last_name", "zip"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "Returns the user_id string if a matching user is found, otherwise returns "
                        "'Error: user not found'. Matching is case-insensitive for first and last name "
                        "and exact-match for ZIP code."
                    ),
                    "examples": [
                        "noah_brown_6181",
                        "ivan_santos_6635",
                        "Error: user not found"
                    ]
                },
            },
        }