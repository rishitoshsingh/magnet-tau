from typing import Any, Dict

from tau_bench.envs.airline.tools.update_reservation_baggages import (
    UpdateReservationBaggages as _UpdateReservationBaggages,
)


class UpdateReservationBaggages(_UpdateReservationBaggages):

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_reservation_baggages",
                "description": "Update the baggage information of a reservation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reservation_id": {
                            "type": "string",
                            "description": "The reservation ID, such as '4WQ150'.",
                        },
                        "total_baggages": {
                            "type": "integer",
                            "description": "The updated total number of baggage items included in the reservation.",
                        },
                        "nonfree_baggages": {
                            "type": "integer",
                            "description": "The updated number of non-free baggage items included in the reservation.",
                        },
                        "payment_id": {
                            "type": "string",
                            "description": "The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.",
                        },
                    },
                    "required": [
                        "reservation_id",
                        "total_baggages",
                        "nonfree_baggages",
                        "payment_id",
                    ],
                },
                "response": {
                    "type": "object",
                    "description": "The updated reservation record after modifying baggage counts and possibly appending a payment entry.",
                    "properties": {
                        "reservation_id": {
                            "type": "string",
                            "description": "The unique ID of the reservation, such as '4WQ150'.",
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
                            "description": "An array of objects containing details about each booked flight segment.",
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
                                        "description": "Flight number, such as 'HAT170'.",
                                    },
                                    "date": {
                                        "type": "string",
                                        "description": "The date for the flight in 'YYYY-MM-DD' format.",
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
                            "description": "Payment entries for the reservation, including any new baggage charge.",
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
                            "description": "ISO 8601 timestamp when the reservation was created, such as '2024-05-02T03:10:19'.",
                        },
                        "total_baggages": {
                            "type": "integer",
                            "description": "The updated total number of baggage items included in the reservation.",
                        },
                        "nonfree_baggages": {
                            "type": "integer",
                            "description": "The updated number of non-free baggage items included in the reservation.",
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