import json
import random

from langchain.tools import tool
from tau_bench.envs.airline.data import load_data

data = load_data()
flights = data["flights"]
reservations = data["reservations"]
users = data["users"]

@tool
def get_all_user_ids() -> list[str]:
    """
    Get all user IDs stored in the airline dataset.

    This returns a shuffled list of all unique user IDs currently
    in the system. Shuffling ensures results are not always in the
    same order.

    Returns:
        A list of user ID strings.
    """
    user_ids = list(users.keys())
    random.shuffle(user_ids)
    return user_ids

@tool
def get_user_details(user_id: str) -> dict:
    """
    Fetch user information for a specific user ID.

    Args:
        user_id: The unique identifier for a user.
    Returns:
        A dictionary of user fields (name, contact info, reservations, passengers.)
        or an empty dict if the ID is not found.
    """
    return users.get(user_id, None)

@tool
def get_reservation_details(reservation_id: str) -> dict:
    """
    Fetch reservation information for a specific reservation ID.

    Args:
        reservation_id: The unique identifier for a reservation.

    Returns:
        A dictionary of reservation fields (user, flights, pricing, etc.)
        or an empty dict if the ID is not found.
    """
    return reservations.get(reservation_id, None)

@tool
def get_flight_details(flight_id: str) -> dict:
    """
    Look up detailed flight information by flight ID.

    Args:
        flight_id: The unique identifier for a flight.

    Returns:
        A dictionary containing the flight metadata including route, times,
        and schedule data or an empty dict if not found.
    """
    return flights.get(flight_id, None)

@tool
def delayed_flights(date: str) -> list[ dict]:
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
    from datetime import datetime
    result = []

    for flight_id, info in flights.items():
        day = info.get("dates", None).get(date)
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

@tool
def cancelled_flights(date: str) -> list[dict]:
    """
    Get flights that were cancelled on a specific date.

    Args:
        date: A string date in ISO format (YYYY-MM-DD) to check for cancelled flights.

    Returns:
        A list of dictionaries, each representing a cancelled flight for that date,
        including basic flight information and the cancellation status.
    """
    result = []
    for flight_id, info in flights.items():
        day = info.get("dates", None).get(date)
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

@tool
def get_reservation_ids_for_flight(flight_id: str, date: str) -> list[str]:
    """
    List all reservation IDs associated with a particular flight on a given date.

    Args:
        flight_id: The unique flight identifier to search within reservation records.
        date: The flight’s scheduled date in ISO format (YYYY-MM-DD).

    Returns:
        A shuffled list of reservation IDs where the flight and date match.
        If none match, returns an empty list.
    """

    result = []
    for res_id, res in reservations.items():
        res_flights = res.get("flights", [])
        for flight in res_flights:
            if flight.get("flight_number") == flight_id and flight.get("date") == date:
                result.append(res_id)
                break
    random.shuffle(result)
    return result

@tool
def verify_search_direct_flight(origin: str, destination: str, date: str) -> list[str]:
    """
    Verify if there are direct flights available between origin and destination on a given date.
    Args:
        origin: The IATA code of the origin airport.
        destination: The IATA code of the destination airport.
        date: The flight’s scheduled date in ISO format (YYYY-MM-DD).
    """
    results = []
    for flight in flights.values():
        if flight["origin"] == origin and flight["destination"] == destination:
            if (
                date in flight["dates"]
                and flight["dates"][date]["status"] == "available"
            ):
                # results add flight except dates, but add flight["datas"][date]
                results.append({k: v for k, v in flight.items() if k != "dates"})
                results[-1].update(flight["dates"][date])
    return json.dumps(results)

@tool
def verify_search_one_stop_flight(origin: str, destination: str, date: str) -> list[str]:
    """
    Verify if there are one-stop flights available between origin and destination on a given date.
    Args:
        origin: The IATA code of the origin airport.
        destination: The IATA code of the destination airport.
        date: The flight’s scheduled date in ISO format (YYYY-MM-DD).
    """
    results = []
    for flight1 in flights.values():
        if flight1["origin"] == origin:
            for flight2 in flights.values():
                if (
                    flight2["destination"] == destination
                    and flight1["destination"] == flight2["origin"]
                ):
                    date2 = (
                        f"2024-05-{int(date[-2:])+1}"
                        if "+1" in flight1["scheduled_arrival_time_est"]
                        else date
                    )
                    if (
                        flight1["scheduled_arrival_time_est"]
                        > flight2["scheduled_departure_time_est"]
                    ):
                        continue
                    if date in flight1["dates"] and date2 in flight2["dates"]:
                        if (
                            flight1["dates"][date]["status"] == "available"
                            and flight2["dates"][date2]["status"] == "available"
                        ):
                            result1 = {
                                k: v for k, v in flight1.items() if k != "dates"
                            }
                            result1.update(flight1["dates"][date])
                            result1["date"] = date
                            result2 = {
                                k: v for k, v in flight2.items() if k != "dates"
                            }
                            result2.update(flight2["dates"][date])
                            result2["date"] = date2
                            results.append([result1, result2])
        return json.dumps(results)

tools = [
    get_all_user_ids,
    get_user_details,
    delayed_flights,
    cancelled_flights,
    get_flight_details,
    get_reservation_ids_for_flight,
    get_reservation_details,
    verify_search_direct_flight,
    verify_search_one_stop_flight,
]

