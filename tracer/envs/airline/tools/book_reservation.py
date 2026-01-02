from typing import Any, Dict

from tau_bench.envs.airline.tools.book_reservation import (
    BookReservation as _BookReservation,
)


class BookReservation(_BookReservation):

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "book_reservation",
                "description": "Book a reservation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user to book the reservation, such as 'sara_doe_496'.",
                        },
                        "origin": {
                            "type": "string",
                            "description": "The IATA code for the origin city, such as 'SFO'.",
                        },
                        "destination": {
                            "type": "string",
                            "description": "The IATA code for the destination city, such as 'JFK'.",
                        },
                        "flight_type": {
                            "type": "string",
                            "enum": ["one_way", "round_trip"],
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
                            "description": "An array of objects containing details about each piece of flight.",
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
                        "passengers": {
                            "type": "array",
                            "description": "An array of objects containing details about each passenger.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "first_name": {
                                        "type": "string",
                                        "description": "The first name of the passenger, such as 'Noah'.",
                                    },
                                    "last_name": {
                                        "type": "string",
                                        "description": "The last name of the passenger, such as 'Brown'.",
                                    },
                                    "dob": {
                                        "type": "string",
                                        "description": "The date of birth of the passenger in the format 'YYYY-MM-DD', such as '1990-01-01'.",
                                    },
                                },
                                "required": ["first_name", "last_name", "dob"],
                            },
                        },
                        "payment_methods": {
                            "type": "array",
                            "description": "An array of objects containing details about each payment method.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "payment_id": {
                                        "type": "string",
                                        "description": "The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.",
                                    },
                                    "amount": {
                                        "type": "number",
                                        "description": "The amount to be paid.",
                                    },
                                },
                                "required": ["payment_id", "amount"],
                            },
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
                        },
                    },
                    "required": [
                        "user_id",
                        "origin",
                        "destination",
                        "flight_type",
                        "cabin",
                        "flights",
                        "passengers",
                        "payment_methods",
                        "total_baggages",
                        "nonfree_baggages",
                        "insurance",
                    ],
                },
                "response": {
                    "type": "object",
                    "description": "Details of the successfully created reservation.",
                    "properties": {
                        "reservation_id": {
                            "type": "string",
                            "description": "The unique ID of the reservation, such as 'HATHAT'.",
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
                            "description": "An array of objects describing how the reservation was paid.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "payment_id": {
                                        "type": "string",
                                        "description": "The payment method ID used for this part of the payment.",
                                    },
                                    "amount": {
                                        "type": "number",
                                        "description": "The amount charged to this payment method.",
                                    },
                                },
                                "required": ["payment_id", "amount"],
                            },
                        },
                        "created_at": {
                            "type": "string",
                            "description": "The ISO 8601 timestamp when the reservation was created, such as '2024-05-15T15:00:00'.",
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