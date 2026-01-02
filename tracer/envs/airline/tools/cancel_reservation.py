from typing import Any, Dict

from tau_bench.envs.airline.tools.cancel_reservation import (
    CancelReservation as _CancelReservation,
)


class CancelReservation(_CancelReservation):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "cancel_reservation",
                "description": "Cancel the whole reservation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reservation_id": {
                            "type": "string",
                            "description": "The reservation ID, such as 'ZFA04Y'.",
                        },
                    },
                    "required": ["reservation_id"],
                },
                "response": {
                    "type": "object",
                    "description": "Details of the reservation after cancellation. On success, the reservation status is updated to 'cancelled' and refund entries are appended to the payment history.",
                    "properties": {
                        "reservation_id": {
                            "type": "string",
                            "description": "The unique ID of the reservation, such as 'HATHAT'.",
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
                                        "description": "The IATA code for the origin city of this segment.",
                                    },
                                    "destination": {
                                        "type": "string",
                                        "description": "The IATA code for the destination city of this segment.",
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
                            "description": "An array of objects containing details about each passenger.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "first_name": {
                                        "type": "string",
                                    },
                                    "last_name": {
                                        "type": "string",
                                    },
                                    "dob": {
                                        "type": "string",
                                        "description": "The date of birth of the passenger in the format 'YYYY-MM-DD'.",
                                    },
                                },
                                "required": ["first_name", "last_name", "dob"],
                            },
                        },
                        "payment_history": {
                            "type": "array",
                            "description": "An array of objects describing all payment and refund entries. Refunds are represented as negative amounts.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "payment_id": {
                                        "type": "string",
                                        "description": "The payment method ID used for this entry.",
                                    },
                                    "amount": {
                                        "type": "number",
                                        "description": "The amount charged (positive) or refunded (negative) for this entry.",
                                    },
                                },
                                "required": ["payment_id", "amount"],
                            },
                        },
                        "created_at": {
                            "type": "string",
                            "description": "The ISO 8601 timestamp when the reservation was originally created, such as '2024-05-15T15:00:00'.",
                        },
                        "total_baggages": {
                            "type": "integer",
                            "description": "The total number of baggage items included in the reservation.",
                        },
                        "nonfree_baggages": {
                            "type": "integer",
                            "description": "The number of non-free baggage items included in the reservation.",
                        },
                        "insurance": {
                            "type": "string",
                            "enum": ["yes", "no"],
                            "description": "Whether travel insurance is included.",
                        },
                        "status": {
                            "type": "string",
                            "description": "The current status of the reservation. After cancellation this will be 'cancelled'.",
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
                        "status",
                    ],
                },
            },
        }