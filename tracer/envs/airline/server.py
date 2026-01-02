# mcp_server.py
from __future__ import annotations

import random
from datetime import datetime
from typing import Any, Dict, List

# FastMCP imports
from fastmcp import FastMCP

# --- load dataset (same as your original) -------------------------------------
from tau_bench.envs.airline.data import load_data

data = load_data()
flights: Dict[str, dict] = data["flights"]
reservations: Dict[str, dict] = data["reservations"]
users: Dict[str, dict] = data["users"]

# --- create FastMCP server instance --------------------------------------------
mcp = FastMCP(name="airline_reverse_tools")

# --- Tools ---------------------------------------------------------------------
# Note: FastMCP will infer parameter schemas from type hints / docstrings.
@mcp.tool(
    name="get_all_user_ids",
    description="Return a shuffled list of all unique user IDs in the dataset."
)
def get_all_user_ids() -> List[str]:
    """
    Get all user IDs stored in the airline dataset.

    Returns:
        A shuffled list of user ID strings.
    """
    user_ids = list(users.keys())
    random.shuffle(user_ids)
    return user_ids


@mcp.tool(
    name="get_reservation_details",
    description="Fetch reservation information for a specific reservation ID."
)
def get_reservation_details(reservation_id: str) -> Dict[str, Any]:
    """
    Fetch reservation information for a specific reservation ID.

    Args:
        reservation_id: The unique identifier for a reservation.

    Returns:
        A dictionary of reservation fields (user, flights, pricing, etc.)
        or an empty dict if the ID is not found.
    """
    return reservations.get(reservation_id, {})


@mcp.tool(
    name="get_flight_details",
    description="Look up detailed flight information by flight ID."
)
def get_flight_details(flight_id: str) -> Dict[str, Any]:
    """
    Look up detailed flight information by flight ID.

    Args:
        flight_id: The unique identifier for a flight.

    Returns:
        A dictionary containing the flight metadata including route, times,
        and schedule data or an empty dict if not found.
    """
    return flights.get(flight_id, {})


@mcp.tool(
    name="delayed_flights",
    description="Find flights that experienced a departure delay on a given date."
)
def delayed_flights(date: str) -> List[Dict[str, Any]]:
    """
    Find flights that experienced a departure delay on a given date.

    A delayed flight is one whose actual departure time (if available)
    occurs strictly after its scheduled departure time.

    Args:
        date: Date in ISO format (YYYY-MM-DD) to check for delays.

    Returns:
        A list of dicts describing each delayed flight and its delay
        duration in minutes.
    """
    result: List[Dict[str, Any]] = []

    for flight_id, info in flights.items():
        day = info.get("dates", {}).get(date)
        if not day or day.get("status") != "landed":
            continue

        actual_iso = day.get("actual_departure_time_est")
        scheduled_time = info.get("scheduled_departure_time_est")
        if not actual_iso or not scheduled_time:
            continue

        try:
            scheduled_dt = datetime.strptime(f"{date}T{scheduled_time}", "%Y-%m-%dT%H:%M:%S")
            actual_dt = datetime.fromisoformat(actual_iso)
        except Exception:
            continue

        if actual_dt <= scheduled_dt:
            continue

        delay_minutes = int((actual_dt - scheduled_dt).total_seconds() // 60)
        result.append(
            {
                "flight_id": flight_id,
                "flight_number": info.get("flight_number"),
                "origin": info.get("origin"),
                "destination": info.get("destination"),
                "date": date,
                "status": day.get("status"),
                "delay_minutes": delay_minutes,
                "details": day,
            }
        )
    random.shuffle(result)
    return result


@mcp.tool(
    name="cancelled_flights",
    description="Get flights that were cancelled on a specific date."
)
def cancelled_flights(date: str) -> List[Dict[str, Any]]:
    """
    Get flights that were cancelled on a specific date.

    Args:
        date: A string date in ISO format (YYYY-MM-DD) to check for cancelled flights.

    Returns:
        A list of dictionaries, each representing a cancelled flight for that date,
        including basic flight information and the cancellation status.
    """
    result: List[Dict[str, Any]] = []
    for flight_id, info in flights.items():
        day = info.get("dates", {}).get(date)
        if not day:
            continue
        if day.get("status") == "cancelled":
            result.append({
                "flight_id": flight_id,
                "flight_number": info.get("flight_number"),
                "origin": info.get("origin"),
                "destination": info.get("destination"),
                "date": date,
                "status": "cancelled",
                "details": day,
            })
    random.shuffle(result)
    return result


@mcp.tool(
    name="get_reservation_ids_for_flight",
    description="List reservation IDs for a given flight number and date."
)
def get_reservation_ids_for_flight(flight_id: str, date: str) -> List[str]:
    """
    List all reservation IDs associated with a particular flight on a given date.

    Args:
        flight_id: The flight number to search (string).
        date: The flight’s scheduled date in ISO format (YYYY-MM-DD).

    Returns:
        A shuffled list of reservation IDs where the flight and date match.
        If none match, returns an empty list.
    """
    result: List[str] = []
    for res_id, res in reservations.items():
        res_flights = res.get("flights", [])
        for flight in res_flights:
            if flight.get("flight_number") == flight_id and flight.get("date") == date:
                result.append(res_id)
                break
    random.shuffle(result)
    return result


# --- optional: utility to invoke tools locally --------------------------------
if __name__ == "__main__":
    mcp.run()    # mcp.run(host="0.0.0.0", port=8000)