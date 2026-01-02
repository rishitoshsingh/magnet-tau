from typing import Any, Dict, List

from tau_bench.envs.airline.tools.update_reservation_flights import (
    UpdateReservationFlights as _UpdateReservationFlights,
)


class UpdateReservationFlights(_UpdateReservationFlights):

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_reservation_flights",
                "description": "Update the flight information of a reservation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reservation_id": {
                            "type": "string",
                            "description": "The reservation ID, such as 'ZFA04Y'.",
                        },
                        "cabin": {
                            "type": "string",
                            "enum": [
                                "basic_economy",
                                "economy",
                                "business",
                            ],
                        },
                        "flights": {
                            "type": "array",
                            "description": "An array of objects containing details about each piece of flight in the ENTIRE new reservation. Even if a flight segment is not changed, it should still be included in the array.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "flight_number": {
                                        "type": "string",
                                        "description": "Flight number, such as 'HAT001'.",
                                    },
                                    "date": {
                                        "type": "string",
                                        "description": "The date for the flight in the format 'YYYY-MM-DD', such as '2024-05-01'.",
                                    },
                                },
                                "required": ["flight_number", "date"],
                            },
                        },
                        "payment_id": {
                            "type": "string",
                            "description": "The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.",
                        },
                    },
                    "required": ["reservation_id", "cabin", "flights", "payment_id"],
                },
                "response": {
                    "type": "object",
                    "description": "The updated reservation after changing its flights and possibly adding a payment entry.",
                    "properties": {
                        "reservation_id": {
                            "type": "string",
                            "description": "The unique ID of the reservation.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user who owns the reservation.",
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
                            "enum": ["basic_economy", "economy", "business"],
                            "description": "The cabin type of the reservation.",
                        },
                        "flights": {
                            "type": "array",
                            "description": "The new list of flight segments in the reservation.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "origin": {
                                        "type": "string",
                                        "description": "Segment origin airport.",
                                    },
                                    "destination": {
                                        "type": "string",
                                        "description": "Segment destination airport.",
                                    },
                                    "flight_number": {
                                        "type": "string",
                                        "description": "Flight number, such as 'HAT001'.",
                                    },
                                    "date": {
                                        "type": "string",
                                        "description": "The date for this segment in 'YYYY-MM-DD' format.",
                                    },
                                    "price": {
                                        "type": "number",
                                        "description": "Price per passenger for this segment in the selected cabin.",
                                    },
                                },
                                "required": [
                                    "origin",
                                    "destination",
                                    "flight_number",
                                    "date",
                                    "price",
                                ],
                            },
                        },
                        "passengers": {
                            "type": "array",
                            "description": "Passenger details for this reservation.",
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
                            "description": "All payment entries for the reservation, including any new charge from the flight update.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "payment_id": {
                                        "type": "string",
                                        "description": "Payment method ID used for this entry.",
                                    },
                                    "amount": {
                                        "type": "number",
                                        "description": "Amount charged (positive) or refunded (negative).",
                                    },
                                },
                                "required": ["payment_id", "amount"],
                            },
                        },
                        "created_at": {
                            "type": "string",
                            "description": "ISO 8601 timestamp when the reservation was created.",
                        },
                        "total_baggages": {
                            "type": "integer",
                            "description": "Total number of baggage items included in the reservation.",
                        },
                        "nonfree_baggages": {
                            "type": "integer",
                            "description": "Number of non-free baggage items.",
                        },
                        "insurance": {
                            "type": "string",
                            "enum": ["yes", "no"],
                            "description": "Whether travel insurance is included.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Current reservation status (e.g., 'cancelled'). May be absent for active reservations.",
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
                        "insurance",
                    ],
                },
            },
        }