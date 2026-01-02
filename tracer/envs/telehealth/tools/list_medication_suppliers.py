from __future__ import annotations

from typing import Any, Dict

from tau_bench.envs.telehealth.tools.list_medication_suppliers import (
    ListMedicationSuppliers as _ListMedicationSuppliers,
)


class ListMedicationSuppliers(_ListMedicationSuppliers):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_medication_suppliers",
                "description": (
                    "List suppliers for a given medication, optionally filtered by country and optionally "
                    "limited to the lowest-cost suppliers. Case-insensitive matching is supported. "
                    "Output is a human-readable multi-line list of suppliers including company, country, "
                    "brand name, and price in USD. If no suppliers are found, returns an informative error message."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "medication": {
                            "type": "string",
                            "description": (
                                "Medication name to search for, such as 'Atorvastatin' or 'Aspirin EC'. "
                                "Must match a key in the medication supplier catalog (case-insensitive)."
                            ),
                        },
                        "country_filter": {
                            "type": "string",
                            "description": (
                                "Optional country name to filter suppliers by (case-insensitive), such as 'India', "
                                "'USA', 'Canada', 'Germany'."
                            ),
                        },
                        "limit": {
                            "type": "integer",
                            "description": (
                                "Optional maximum number of suppliers to return. If provided, suppliers are sorted "
                                "by price and the lowest-cost results are returned."
                            ),
                        },
                    },
                    "required": ["medication"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "A multi-line formatted string listing suppliers for the requested medication. "
                        "Each supplier entry contains: company, country, brand name, and price in USD. "
                        "If no suppliers are found—or if country filtering eliminates all results—an "
                        "error-like string is returned instead."
                    ),
                    "examples": [
                        # Successful full response for Atorvastatin
                        (
                            "Suppliers for Atorvastatin:\n"
                            "Sunrise Biotech (India) | brand=Lipistal | price_usd=4.15\n"
                            "VedaRx Labs (India) | brand=Atorveeda | price_usd=4.05\n"
                            "Bharat Lifecare (India) | brand=Cholozen | price_usd=4.30\n"
                            "Lagos Pharma (Nigeria) | brand=Atorlag | price_usd=5.95\n"
                            "Qianlong Remedies (China) | brand=LongStat | price_usd=5.40\n"
                            "MedFirst Generics (USA) | brand=StatGuard | price_usd=6.80\n"
                            "Pacific Coast Labs (USA) | brand=CoastStat | price_usd=6.55\n"
                            "Silver Maple Pharma (Canada) | brand=MapleStat | price_usd=6.20\n"
                            "Trinity Generics (UK) | brand=Cardiotor | price_usd=6.45\n"
                            "NovaNord Therapeutics (Denmark) | brand=AtorvaNova | price_usd=7.10"
                        ),

                        # Country-filtered example
                        (
                            "Suppliers for Atorvastatin:\n"
                            "VedaRx Labs (India) | brand=Atorveeda | price_usd=4.05\n"
                            "Sunrise Biotech (India) | brand=Lipistal | price_usd=4.15\n"
                            "Bharat Lifecare (India) | brand=Cholozen | price_usd=4.30"
                        ),

                        # Limited example (cheapest 2)
                        (
                            "Suppliers for Metoprolol Succinate:\n"
                            "Aurora Heart Labs (India) | brand=BetaShield | price_usd=3.80\n"
                            "MedNova Kerala (India) | brand=Metotime | price_usd=3.95"
                        ),

                        # Error: medication not found
                        "No supplier information found for Xylostat. (Tip: ensure the medication name matches the catalog)",

                        # Error: filtering removes all suppliers
                        "No suppliers in Germany for Aspirin EC."
                    ],
                },
            },
        }  