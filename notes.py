types of data:
1. Single goal - Declarative, procedural
2. Multiple goals - Procedural and declarative


=> Multiple goal in single query


TASKS:
1. Find best Paths
2. Find the data for best paths
3. Install VERL on 10.
4. Setup Env for RL
5. Find benchmarks for personas



# Tried for following trace:
[[
      {
        "idx": 1,
        "name": "CancelReservation",
        "info": {
          "type": "function",
          "function": {
            "name": "cancel_reservation",
            "description": "Cancel the whole reservation.",
            "parameters": {
              "type": "object",
              "properties": {
                "reservation_id": {
                  "type": "string",
                  "description": "The reservation ID, such as 'ZFA04Y'."
                }
              },
              "required": [
                "reservation_id"
              ]
            },
            "response": {
              "type": "object",
              "description": "Details of the reservation after cancellation. On success, the reservation status is updated to 'cancelled' and refund entries are appended to the payment history.",
              "properties": {
                "reservation_id": {
                  "type": "string",
                  "description": "The unique ID of the reservation, such as 'HATHAT'."
                },
                "user_id": {
                  "type": "string",
                  "description": "The ID of the user who owns the reservation."
                },
                "origin": {
                  "type": "string",
                  "description": "The IATA code for the origin city."
                },
                "destination": {
                  "type": "string",
                  "description": "The IATA code for the destination city."
                },
                "flight_type": {
                  "type": "string",
                  "enum": [
                    "one_way",
                    "round_trip"
                  ],
                  "description": "The type of trip."
                },
                "cabin": {
                  "type": "string",
                  "enum": [
                    "basic_economy",
                    "economy",
                    "business"
                  ],
                  "description": "The cabin type of the reservation."
                },
                "flights": {
                  "type": "array",
                  "description": "An array of objects containing details about each booked flight segment.",
                  "items": {
                    "type": "object",
                    "properties": {
                      "flight_number": {
                        "type": "string",
                        "description": "Flight number, such as 'HAT001'."
                      },
                      "date": {
                        "type": "string",
                        "description": "The date for the flight in the format 'YYYY-MM-DD'."
                      },
                      "origin": {
                        "type": "string",
                        "description": "The IATA code for the origin city of this segment."
                      },
                      "destination": {
                        "type": "string",
                        "description": "The IATA code for the destination city of this segment."
                      },
                      "price": {
                        "type": "number",
                        "description": "The price per passenger for this segment in the selected cabin."
                      }
                    },
                    "required": [
                      "flight_number",
                      "date",
                      "origin",
                      "destination",
                      "price"
                    ]
                  }
                },
                "passengers": {
                  "type": "array",
                  "description": "An array of objects containing details about each passenger.",
                  "items": {
                    "type": "object",
                    "properties": {
                      "first_name": {
                        "type": "string"
                      },
                      "last_name": {
                        "type": "string"
                      },
                      "dob": {
                        "type": "string",
                        "description": "The date of birth of the passenger in the format 'YYYY-MM-DD'."
                      }
                    },
                    "required": [
                      "first_name",
                      "last_name",
                      "dob"
                    ]
                  }
                },
                "payment_history": {
                  "type": "array",
                  "description": "An array of objects describing all payment and refund entries. Refunds are represented as negative amounts.",
                  "items": {
                    "type": "object",
                    "properties": {
                      "payment_id": {
                        "type": "string",
                        "description": "The payment method ID used for this entry."
                      },
                      "amount": {
                        "type": "number",
                        "description": "The amount charged (positive) or refunded (negative) for this entry."
                      }
                    },
                    "required": [
                      "payment_id",
                      "amount"
                    ]
                  }
                },
                "created_at": {
                  "type": "string",
                  "description": "The ISO 8601 timestamp when the reservation was originally created, such as '2024-05-15T15:00:00'."
                },
                "total_baggages": {
                  "type": "integer",
                  "description": "The total number of baggage items included in the reservation."
                },
                "nonfree_baggages": {
                  "type": "integer",
                  "description": "The number of non-free baggage items included in the reservation."
                },
                "insurance": {
                  "type": "string",
                  "enum": [
                    "yes",
                    "no"
                  ],
                  "description": "Whether travel insurance is included."
                },
                "status": {
                  "type": "string",
                  "description": "The current status of the reservation. After cancellation this will be 'cancelled'."
                }
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
                "status"
              ]
            }
          }
        },
        "is_root": true,
        "is_root_reason": "A customer can reasonably start a support interaction by asking to cancel a booking and providing their reservation_id (often from an email/itinerary). Other required policy prerequisites (reason for cancellation and explicit confirmation) can be collected conversationally without additional domain tools.",
        "neighbors": [
          0,
          2,
          3,
          4
        ],
        "neighbor_reasons": {
          "0": "After cancelling, a common next step is the customer wanting to rebook a new trip; the agent would start a new booking. Inputs needed from user: user_id, origin, destination, flight_type, cabin, preferred flights (flight_number/date), passenger names/DOBs, payment_ids/amounts, bag counts, insurance yes/no.",
          "2": "Agent may immediately fetch the cancelled record to confirm status and read back refund/payment_history details. Input needed: reservation_id.",
          "3": "Customer often asks for alternative flights right after cancelling (or cancels to rebook); searching direct options is a natural next action. Inputs needed: origin, destination, date.",
          "4": "If no direct flights work, searching one-stop itineraries is a typical follow-up to help the customer rebook after cancellation. Inputs needed: origin, destination, date."
        }
      },
      {
        "idx": 2,
        "name": "GetReservationDetails",
        "info": {
          "type": "function",
          "function": {
            "name": "get_reservation_details",
            "description": "Get the details of a reservation.",
            "parameters": {
              "type": "object",
              "properties": {
                "reservation_id": {
                  "type": "string",
                  "description": "The reservation id, such as '8JX2WO'."
                }
              },
              "required": [
                "reservation_id"
              ]
            },
            "response": {
              "type": "object",
              "description": "The complete reservation record as stored in the system.",
              "properties": {
                "reservation_id": {
                  "type": "string",
                  "description": "The unique ID of the reservation."
                },
                "user_id": {
                  "type": "string",
                  "description": "The ID of the user who made the reservation."
                },
                "origin": {
                  "type": "string",
                  "description": "The IATA code for the origin city."
                },
                "destination": {
                  "type": "string",
                  "description": "The IATA code for the destination city."
                },
                "flight_type": {
                  "type": "string",
                  "enum": [
                    "one_way",
                    "round_trip"
                  ],
                  "description": "The type of trip."
                },
                "cabin": {
                  "type": "string",
                  "enum": [
                    "basic_economy",
                    "economy",
                    "business"
                  ],
                  "description": "The cabin type of the reservation."
                },
                "flights": {
                  "type": "array",
                  "description": "An array of objects containing details about each booked flight segment.",
                  "items": {
                    "type": "object",
                    "properties": {
                      "flight_number": {
                        "type": "string",
                        "description": "Flight number, such as 'HAT001'."
                      },
                      "date": {
                        "type": "string",
                        "description": "The date for the flight in the format 'YYYY-MM-DD'."
                      },
                      "origin": {
                        "type": "string",
                        "description": "The origin airport for this segment."
                      },
                      "destination": {
                        "type": "string",
                        "description": "The destination airport for this segment."
                      },
                      "price": {
                        "type": "number",
                        "description": "The price per passenger for this segment in the selected cabin."
                      }
                    },
                    "required": [
                      "flight_number",
                      "date",
                      "origin",
                      "destination",
                      "price"
                    ]
                  }
                },
                "passengers": {
                  "type": "array",
                  "description": "An array of passenger details.",
                  "items": {
                    "type": "object",
                    "properties": {
                      "first_name": {
                        "type": "string"
                      },
                      "last_name": {
                        "type": "string"
                      },
                      "dob": {
                        "type": "string",
                        "description": "Date of birth in 'YYYY-MM-DD' format."
                      }
                    },
                    "required": [
                      "first_name",
                      "last_name",
                      "dob"
                    ]
                  }
                },
                "payment_history": {
                  "type": "array",
                  "description": "Full payment activity including refunds (negative amounts).",
                  "items": {
                    "type": "object",
                    "properties": {
                      "payment_id": {
                        "type": "string",
                        "description": "The payment method ID used."
                      },
                      "amount": {
                        "type": "number",
                        "description": "Positive for charges, negative for refunds."
                      }
                    },
                    "required": [
                      "payment_id",
                      "amount"
                    ]
                  }
                },
                "created_at": {
                  "type": "string",
                  "description": "ISO timestamp when the reservation was created."
                },
                "total_baggages": {
                  "type": "integer",
                  "description": "Total number of baggage items included."
                },
                "nonfree_baggages": {
                  "type": "integer",
                  "description": "Number of paid baggage items."
                },
                "insurance": {
                  "type": "string",
                  "enum": [
                    "yes",
                    "no"
                  ],
                  "description": "Whether insurance was included."
                },
                "status": {
                  "type": "string",
                  "description": "Reservation status (e.g., 'cancelled' after cancellation)."
                }
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
              ]
            }
          }
        },
        "is_root": true,
        "is_root_reason": "A customer commonly contacts support to view/verify an itinerary or charges and can provide the reservation_id directly (e.g., from a confirmation email). No additional domain-specific discovery is required to make the first meaningful action this lookup.",
        "neighbors": [
          1,
          3,
          4,
          6,
          7,
          8
        ],
        "neighbor_reasons": {
          "1": "Common follow-up when a user asks to cancel: agent fetches reservation details to verify cabin/insurance/segments, then proceeds to cancel once the user confirms. User-provided inputs: reservation_id (and separately collected per policy: cancellation reason and explicit confirmation).",
          "3": "After retrieving the reservation, the next step for a change request is often searching alternatives matching the same route/date(s) from the booked segment(s). Inputs: origin, destination, date (from the reservation; agent may confirm which segment/date to change).",
          "4": "If the user wants options that require a connection (or no direct flights exist), the agent would search one-stop itineraries after reviewing the booked segment details. Inputs: origin, destination, date (from the reservation; agent may confirm which leg/date to change).",
          "6": "If the user wants to add checked bags, the agent would review current baggage counts in the reservation details, then update baggage and charge the selected payment method after explicit confirmation. Inputs: reservation_id, new total_baggages, new nonfree_baggages, payment_id.",
          "7": "If the user requests to change flights or cabin (and rules allow), the agent would inspect current itinerary/cabin in the details, then apply the flight update after user confirms and provides a payment/refund method. Inputs: reservation_id, new cabin, full new flights list (flight_number/date), payment_id.",
          "8": "If the user needs to correct passenger name/DOB (without changing passenger count), the agent would first pull current passenger list, then submit the corrected list. Inputs: reservation_id and updated passengers array (first_name, last_name, dob) after explicit confirmation."
        }
      }
    ],
    [
      {
        "idx": 5,
        "name": "SendCertificate",
        "info": {
          "type": "function",
          "function": {
            "name": "send_certificate",
            "description": "Send a certificate to a user as a compensation for a specific complaint filed by the user, which could be flight delay or flight got canceled. It can only be called first not after any other function even if the function have the required parameters for this function.",
            "parameters": {
              "type": "object",
              "properties": {
                "user_id": {
                  "type": "string",
                  "description": "The ID of the user to receive the certificate as compensation, such as 'sara_doe_496'."
                },
                "amount": {
                  "type": "number",
                  "description": "Certificate amount to send as compensation."
                }
              },
              "required": [
                "user_id",
                "amount"
              ]
            },
            "response": {
              "type": "string",
              "description": "A human-readable message. On success: 'Certificate <certificate_id> added to user <user_id> with amount <amount>.' On failure: 'Error: user not found'.",
              "examples": [
                "Certificate certificate_3221322 added to user mia_li_3668 with amount 100.",
                "Error: user not found"
              ]
            }
          }
        },
        "is_root": true,
        "is_root_reason": "A customer can directly ask for compensation for a delay/cancellation, and the agent can issue the certificate as the first meaningful action once the user is identified. The required inputs (user_id and a stated/eligible compensation amount) are available/derivable at the start of the interaction.",
        "neighbors": [],
        "neighbor_reasons": {}
      }
    ]
]
GPT5.2 came upi with:
USER: amelia_li_7843, TO cancel reservation UUMFG6 as one flight in that reservation was canceled.

User (for SendCertificate): amelia_li_7843
Reservation to cancel (CancelReservation): UUMFG6
Reservation referenced for compensation: UUMFG6 (same booking; affected by airline disruption)
Why this is “eligible” compensation data (airline-caused):

Reservation UUMFG6 includes flight HAT205 on 2024-05-03
Flight HAT205 on 2024-05-03 has status cancelled (airline cancellation)
Reservation UUMFG6 key details

Route: BOS -> CLT -> PHL
Flights: HAT260 (2024-05-03), HAT205 (2024-05-03, cancelled)
Passenger: Amelia Li (DOB 1976-03-08)
Cabin: economy


SAMPLE 2:
SEND CERTIFICATE -> SEARCH_DIRECCT, BOOKRESERVATION

Prompt:
the selected list of tools are part of a customer you will call the customer agent for a problem or a series of problem (Represented by nunmber of lists) The goal is to generate a dataset for which the agent will call the selected tools in given sequence. Your goal is to find the user_id who will call for some problem, use airline_reverse_tools to reverse engineer the date and find perdfect data and story of user goal

Output:
{
  "problem_id": "airline_cancelled_connection_send_certificate_first",
  "user_id": "evelyn_smith_6580",
  "user_goal": "I’m stranded in DFW because my connection to EWR was cancelled. Please help me get to EWR ASAP and compensate me for the disruption.",
  "context": {
    "date": "2024-05-11",
    "reservation_id": "432XFH",
    "itinerary": [
      { "flight_number": "HAT297", "origin": "ATL", "destination": "DFW", "date": "2024-05-11", "status": "landed" },
      { "flight_number": "HAT063", "origin": "DFW", "destination": "EWR", "date": "2024-05-11", "status": "cancelled" }
    ],
    "cabin": "economy",
    "trip_type": "one_way",
    "payment": { "method": "gift_card", "id": "gift_card_3816522", "amount": 315 },
    "insurance": "yes"
  },
  "expected_tool_sequence": [
    "SendCertificate",
    "GetReservationDetails",
    "GetFlightDetails",
    "SearchDirectFlight",
    "UpdateReservation"
  ],
  "tool_sequence_constraints": {
    "SendCertificate": "must_be_first"
  },
  "certificate_policy_for_this_case": {
    "reason": "Cancelled connection (customer stranded mid-itinerary)",
    "amount_usd": 150
  },
  "success_criteria": [
    "Agent confirms reservation 432XFH belongs to evelyn_smith_6580",
    "Agent confirms HAT063 is cancelled on 2024-05-11",
    "Agent finds an alternative DFW→EWR option and updates the existing reservation (or, if none exist, clearly explains next-best resolution path)"
  ]
}

