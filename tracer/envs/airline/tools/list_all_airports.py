from typing import Any, Dict

from tau_bench.envs.airline.tools.list_all_airports import (
    ListAllAirports as _ListAllAirports,
)


class ListAllAirports(_ListAllAirports):

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_all_airports",
                "description": "List all airports and their corresponding cities.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
                "response": {
                    "type": "object",
                    "description": "A dictionary mapping airport IATA codes to their city names.",
                    "additionalProperties": {
                        "type": "string",
                        "description": "The name of the city associated with the airport.",
                    },
                    "example": {
                        "SFO": "San Francisco",
                        "JFK": "New York",
                        "LAX": "Los Angeles",
                        "ORD": "Chicago",
                        "DFW": "Dallas",
                        "DEN": "Denver",
                        "SEA": "Seattle",
                        "ATL": "Atlanta",
                        "MIA": "Miami",
                        "BOS": "Boston",
                        "PHX": "Phoenix",
                        "IAH": "Houston",
                        "LAS": "Las Vegas",
                        "MCO": "Orlando",
                        "EWR": "Newark",
                        "CLT": "Charlotte",
                        "MSP": "Minneapolis",
                        "DTW": "Detroit",
                        "PHL": "Philadelphia",
                        "LGA": "LaGuardia"
                    }
                },
            },
        }