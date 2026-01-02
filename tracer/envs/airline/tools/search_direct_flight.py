from typing import Any, Dict

from tau_bench.envs.airline.tools.search_direct_flight import (
    SearchDirectFlight as _SearchDirectFlight,
)


class SearchDirectFlight(_SearchDirectFlight):

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "search_direct_flight",
                "description": "Search direct flights between two cities on a specific date.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "The origin city airport in three letters, such as 'JFK'.",
                        },
                        "destination": {
                            "type": "string",
                            "description": "The destination city airport in three letters, such as 'LAX'.",
                        },
                        "date": {
                            "type": "string",
                            "description": "The date of the flight in the format 'YYYY-MM-DD', such as '2024-01-01'.",
                        },
                    },
                    "required": ["origin", "destination", "date"],
                },
                "response": {
                    "type": "array",
                    "description": "A list of direct flights matching origin, destination and date, including schedule, availability, and prices. Empty list if no flights are available.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "flight_number": {
                                "type": "string",
                                "description": "The flight number, such as 'HAT001'.",
                            },
                            "origin": {
                                "type": "string",
                                "description": "The origin airport IATA code, such as 'PHL'.",
                            },
                            "destination": {
                                "type": "string",
                                "description": "The destination airport IATA code, such as 'LGA'.",
                            },
                            "scheduled_departure_time_est": {
                                "type": "string",
                                "description": "Scheduled departure time in Eastern Time, format 'HH:MM:SS', such as '06:00:00'.",
                            },
                            "scheduled_arrival_time_est": {
                                "type": "string",
                                "description": "Scheduled arrival time in Eastern Time, format 'HH:MM:SS', such as '07:00:00'.",
                            },
                            "status": {
                                "type": "string",
                                "enum": ["available"],
                                "description": "The status for this flight on the requested date. Only 'available' flights are returned.",
                            },
                            "available_seats": {
                                "type": "object",
                                "description": "Number of remaining seats for each cabin on the requested date.",
                                "properties": {
                                    "basic_economy": {
                                        "type": "integer",
                                    },
                                    "economy": {
                                        "type": "integer",
                                    },
                                    "business": {
                                        "type": "integer",
                                    },
                                },
                                "required": [
                                    "basic_economy",
                                    "economy",
                                    "business",
                                ],
                            },
                            "prices": {
                                "type": "object",
                                "description": "Price per passenger in each cabin on the requested date.",
                                "properties": {
                                    "basic_economy": {
                                        "type": "number",
                                    },
                                    "economy": {
                                        "type": "number",
                                    },
                                    "business": {
                                        "type": "number",
                                    },
                                },
                                "required": [
                                    "basic_economy",
                                    "economy",
                                    "business",
                                ],
                            },
                        },
                        "required": [
                            "flight_number",
                            "origin",
                            "destination",
                            "scheduled_departure_time_est",
                            "scheduled_arrival_time_est",
                            "status",
                            "available_seats",
                            "prices",
                        ],
                    },
                },
            },
        }