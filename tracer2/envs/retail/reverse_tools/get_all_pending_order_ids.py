import json
from typing import Any, Dict
import random

from tracer2.envs.tool import Tool


class GetAllPendingOrderIds(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
    ) -> str:
        orders = data["orders"]
        pending_orders = [order_id for order_id, order_data in orders.items() if order_data["status"] == "pending"]
        random.shuffle(pending_orders)
        return json.dumps(pending_orders)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_all_pending_order_ids_shuffled",
                "description": "Get a shuffled list of all pending order IDs currently in the system. This function takes no parameters.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        }