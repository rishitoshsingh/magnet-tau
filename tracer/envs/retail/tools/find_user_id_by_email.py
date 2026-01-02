from typing import Any, Dict

from tau_bench.envs.retail.tools.find_user_id_by_email import (
    FindUserIdByEmail as _FindUserIdByEmailTool,
)


class FindUserIdByEmail(_FindUserIdByEmailTool):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "find_user_id_by_email",
                "description": "Find user id by email. If the user is not found, the function will return an error message.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "The email of the user, such as 'something@example.com'.",
                        },
                    },
                    "required": ["email"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "Returns the user_id string if the email exists in the system, "
                        "otherwise returns the string 'Error: user not found'."
                    ),
                    "examples": [
                        "noah_brown_6181",
                        "ivan_santos_6635",
                        "Error: user not found"
                    ]
                }
            },
        }