import json
from typing import Any, Dict
import random

from tracer2.envs.tool import Tool


class GetAllUserIds(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
    ) -> str:
        users = data["users"]
        user_ids = list(users.keys())
        random.shuffle(user_ids)
        return json.dumps(user_ids)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_all_user_ids",
                "description": (
                    "Get a shuffled list of all unique user IDs currently in the system. "
                    "This function takes no parameters."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        }