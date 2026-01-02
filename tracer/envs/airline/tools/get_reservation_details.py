from typing import Any, Dict

from tau_bench.envs.airline.tools.get_reservation_details import (
    GetReservationDetails as _GetReservationDetails,
)


class GetReservationDetails(_GetReservationDetails):

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_reservation_details",
                "description": "Get the details of a reservation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reservation_id": {
                            "type": "string",
                            "description": "The reservation id, such as '8JX2WO'.",
                        },
                    },
                    "required": ["reservation_id"],
                },
                "response": {
                    "type": "object",
                    "description": "The complete reservation record as stored in the system.",
                    "properties": {
                        "reservation_id": {
                            "type": "string",
                            "description": "The unique ID of the reservation.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user who made the reservation.",
                        },
                        "origin": {
                            "type": "string",
                            "description": "The IATA code for the origin city.",
                        },
                        "destination": {
                            "type": "string",
                            "description": "The IATA code for the destination city.",
                        },
                        "flight_type": {
                            "type": "string",
                            "enum": ["one_way", "round_trip"],
                            "description": "The type of trip.",
                        },
                        "cabin": {
                            "type": "string",
                            "enum": [
                                "basic_economy",
                                "economy",
                                "business",
                            ],
                            "description": "The cabin type of the reservation.",
                        },
                        "flights": {
                            "type": "array",
                            "description": "An array of objects containing details about each booked flight segment.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "flight_number": {
                                        "type": "string",
                                        "description": "Flight number, such as 'HAT001'.",
                                    },
                                    "date": {
                                        "type": "string",
                                        "description": "The date for the flight in the format 'YYYY-MM-DD'.",
                                    },
                                    "origin": {
                                        "type": "string",
                                        "description": "The origin airport for this segment.",
                                    },
                                    "destination": {
                                        "type": "string",
                                        "description": "The destination airport for this segment.",
                                    },
                                    "price": {
                                        "type": "number",
                                        "description": "The price per passenger for this segment in the selected cabin.",
                                    },
                                },
                                "required": [
                                    "flight_number",
                                    "date",
                                    "origin",
                                    "destination",
                                    "price",
                                ],
                            },
                        },
                        "passengers": {
                            "type": "array",
                            "description": "An array of passenger details.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "first_name": {"type": "string"},
                                    "last_name": {"type": "string"},
                                    "dob": {
                                        "type": "string",
                                        "description": "Date of birth in 'YYYY-MM-DD' format.",
                                    },
                                },
                                "required": ["first_name", "last_name", "dob"],
                            },
                        },
                        "payment_history": {
                            "type": "array",
                            "description": "Full payment activity including refunds (negative amounts).",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "payment_id": {
                                        "type": "string",
                                        "description": "The payment method ID used.",
                                    },
                                    "amount": {
                                        "type": "number",
                                        "description": "Positive for charges, negative for refunds.",
                                    },
                                },
                                "required": ["payment_id", "amount"],
                            },
                        },
                        "created_at": {
                            "type": "string",
                            "description": "ISO timestamp when the reservation was created.",
                        },
                        "total_baggages": {
                            "type": "integer",
                            "description": "Total number of baggage items included.",
                        },
                        "nonfree_baggages": {
                            "type": "integer",
                            "description": "Number of paid baggage items.",
                        },
                        "insurance": {
                            "type": "string",
                            "enum": ["yes", "no"],
                            "description": "Whether insurance was included.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Reservation status (e.g., 'cancelled' after cancellation).",
                        },
                    },
                    "required": [
                        "reservation_id",
                        "user_id",
                        "origin",
                        "destination",
                        "flight_type",
                        "cabin",
                        "flights",
                        "passengers",
                        "payment_history",
                        "created_at",
                        "total_baggages",
                        "nonfree_baggages",
                        "insurance"
                        # "status" is *not* required because original reservations may not have it
                    ],
                },
            },
        }