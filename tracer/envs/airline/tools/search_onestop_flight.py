from typing import Any, Dict

from tau_bench.envs.airline.tools.search_onestop_flight import (
    SearchOnestopFlight as _SearchOnestopFlight,
)


class SearchOnestopFlight(_SearchOnestopFlight):

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "search_onestop_flight",
                "description": "Search one-stop flights between two cities on a specific date.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "The origin airport IATA code, such as 'JFK'.",
                        },
                        "destination": {
                            "type": "string",
                            "description": "The destination airport IATA code, such as 'LAX'.",
                        },
                        "date": {
                            "type": "string",
                            "description": "The flight date in 'YYYY-MM-DD' format, such as '2024-05-01'.",
                        },
                    },
                    "required": ["origin", "destination", "date"],
                },
                "response": {
                    "type": "array",
                    "description": "A list of one-stop itineraries. Each itinerary contains two flight segments, each with schedule, availability, prices, and date.",
                    "items": {
                        "type": "array",
                        "description": "A two-flight itinerary: [first_leg, second_leg].",
                        "minItems": 2,
                        "maxItems": 2,
                        "items": {
                            "type": "object",
                            "properties": {
                                "flight_number": {
                                    "type": "string",
                                    "description": "Flight number, such as 'HAT001'.",
                                },
                                "origin": {
                                    "type": "string",
                                    "description": "Segment origin airport.",
                                },
                                "destination": {
                                    "type": "string",
                                    "description": "Segment destination airport.",
                                },
                                "scheduled_departure_time_est": {
                                    "type": "string",
                                    "description": "Scheduled departure time (EST), format 'HH:MM:SS'.",
                                },
                                "scheduled_arrival_time_est": {
                                    "type": "string",
                                    "description": "Scheduled arrival time (EST), format 'HH:MM:SS'.",
                                },
                                "date": {
                                    "type": "string",
                                    "description": "Flight date used for this segment. The second segment may be '+1 day' depending on arrival time logic.",
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["available"],
                                    "description": "Status for this flight on its date. Only 'available' flights are returned.",
                                },
                                "available_seats": {
                                    "type": "object",
                                    "properties": {
                                        "basic_economy": {"type": "integer"},
                                        "economy": {"type": "integer"},
                                        "business": {"type": "integer"},
                                    },
                                    "required": [
                                        "basic_economy",
                                        "economy",
                                        "business"
                                    ],
                                    "description": "Seat availability for the given segment date.",
                                },
                                "prices": {
                                    "type": "object",
                                    "properties": {
                                        "basic_economy": {"type": "number"},
                                        "economy": {"type": "number"},
                                        "business": {"type": "number"},
                                    },
                                    "required": [
                                        "basic_economy",
                                        "economy",
                                        "business"
                                    ],
                                    "description": "Price per passenger for each cabin.",
                                },
                            },
                            "required": [
                                "flight_number",
                                "origin",
                                "destination",
                                "scheduled_departure_time_est",
                                "scheduled_arrival_time_est",
                                "date",
                                "status",
                                "available_seats",
                                "prices",
                            ],
                        },
                    },
                },
            },
        }