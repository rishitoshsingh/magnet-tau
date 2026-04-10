import json
import random
from typing import Any, Dict, List, Optional

from tracer3.envs.tool import Tool

# Max number of users to return per call (paginated batch)
_MAX_USERS = 5

_call_counter = 0


def _user_ids_filtered_by_status(
    data: Dict[str, Any],
    status_filter: Optional[str],
) -> List[str]:
    """Return user_ids that have at least one order. If status_filter is 'pending' or 'delivered', only users with at least one order of that status."""
    users = data["users"]
    orders = data["orders"]
    result = []
    for user_id, user in users.items():
        order_ids = user.get("orders", [])
        if not order_ids:
            continue
        if status_filter is None:
            result.append(user_id)
        elif any(orders.get(oid, {}).get("status") == status_filter for oid in order_ids):
            result.append(user_id)
    return result


def _counts_by_status(data: Dict[str, Any], user_id: str) -> Dict[str, int]:
    users = data["users"]
    orders = data["orders"]
    order_ids = users.get(user_id, {}).get("orders", [])
    counts = {"delivered": 0, "pending": 0, "cancelled": 0, "processed": 0}
    for oid in order_ids:
        status = orders.get(oid, {}).get("status")
        if status in counts:
            counts[status] += 1
    return counts


class GetUsersWithOrders(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        status: Optional[str] = None,
    ) -> str:
        global _call_counter
        users = data["users"]
        user_ids = _user_ids_filtered_by_status(data, status)
        random.shuffle(user_ids)
        if not user_ids:
            return json.dumps([])
        offset = (_call_counter * _MAX_USERS) % len(user_ids)
        _call_counter += 1
        ids_doubled = user_ids + user_ids
        batch_ids = ids_doubled[offset : offset + _MAX_USERS]
        result = []
        for uid in batch_ids:
            order_ids = users[uid].get("orders", [])
            counts = _counts_by_status(data, uid)
            result.append({
                "user_id": uid,
                "total_orders": len(order_ids),
                "delivered_count": counts["delivered"],
                "pending_count": counts["pending"],
                "cancelled_count": counts["cancelled"],
            })
        return json.dumps(result)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_users_with_orders",
                "description": (
                    "Get users who have at least one order. "
                    "Returns for each user: user_id, total_orders, delivered_count, pending_count, cancelled_count (no full user or order details). "
                    "Optional parameter status: if 'pending' or 'delivered', only return users who have at least one order with that status. "
                    "Results are randomized; each call returns up to 5 users with a rotating offset."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["pending", "delivered"],
                            "description": "Optional. If provided, only return users who have at least one order with this status.",
                        },
                    },
                    "required": [],
                },
            },
        }
