from typing import Any, Dict

from tau_bench.envs.telehealth.tools.update_prescription_supplier import (
    UpdatePrescriptionSupplier as _UpdatePrescriptionSupplier,
)


class UpdatePrescriptionSupplier(_UpdatePrescriptionSupplier):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_prescription_supplier",
                "description": (
                    "Update the supplier information for a specific prescription entry in a medical record.\n\n"
                    "Behavior:\n"
                    "- Looks up the record in data['medical_records'] by record_id.\n"
                    "- If the record does not exist, returns: 'Error: medical record not found'.\n"
                    "- Checks that the record has a non-empty 'prescriptions' list; if not, returns: "
                    "'Error: medical record has no prescriptions'.\n"
                    "- Attempts to find the target prescription by medication name:\n"
                    "  * Builds a case-insensitive map of existing prescription['medication'] values.\n"
                    "  * First tries an exact (case-insensitive) match.\n"
                    "  * If no exact match, tries a partial match to handle names with appended dosage "
                    "like 'Sertraline 75mg once daily'.\n"
                    "- If no matching medication is found, returns: "
                    "'Error: medication <medication> not found in record <record_id>'.\n"
                    "- On a match, updates that prescription with:\n"
                    "  * pharmacy = '<supplier_company> (<brand_name>)'\n"
                    "  * supplier = {company, brand_name, price_usd, currency}\n"
                    "- Returns the full updated medical record as a JSON string."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "record_id": {
                            "type": "string",
                            "description": (
                                "The medical record identifier to update, e.g. 'REC001'. "
                                "Must exist in data['medical_records'] or an error is returned."
                            ),
                        },
                        "medication": {
                            "type": "string",
                            "description": (
                                "Name of the medication whose prescription entry should be updated, "
                                "e.g. 'Sertraline'. Matching is case-insensitive and can tolerate "
                                "extra dosage text like 'Sertraline 75mg once daily'."
                            ),
                        },
                        "supplier_company": {
                            "type": "string",
                            "description": (
                                "Name of the supplier company providing the medication, "
                                "e.g. 'Sunrise Biotech'."
                            ),
                        },
                        "brand_name": {
                            "type": "string",
                            "description": (
                                "Brand name used by the supplier for this medication, "
                                "e.g. 'Lipistal'. This will be shown in the 'pharmacy' field as "
                                "'<supplier_company> (<brand_name>)'."
                            ),
                        },
                        "price_usd": {
                            "type": "number",
                            "description": (
                                "Unit price from the supplier catalog, expressed in USD by default. "
                                "Will be stored as a float under supplier.price_usd."
                            ),
                        },
                        "currency": {
                            "type": "string",
                            "description": (
                                "Currency code for the quoted price, e.g. 'USD', 'EUR'. "
                                "Defaults to 'USD' if not provided."
                            ),
                            "default": "USD",
                        },
                    },
                    "required": [
                        "record_id",
                        "medication",
                        "supplier_company",
                        "brand_name",
                        "price_usd",
                    ],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "On success: JSON string of the full updated medical record, including the modified "
                        "prescription with 'pharmacy' and 'supplier' fields set.\n"
                        "On failure: one of the error strings:\n"
                        "- 'Error: medical record not found'\n"
                        "- 'Error: medical record has no prescriptions'\n"
                        "- 'Error: medication <medication> not found in record <record_id>'"
                    ),
                    "examples": [
                        # Success (shape reflecting the provided sample)
                        (
                            '{\n'
                            '  "record_id": "REC001",\n'
                            '  "appointment_id": "APPT002",\n'
                            '  "patient_id": "david_martinez_5678",\n'
                            '  "provider_id": "dr_williams_psychiatry",\n'
                            '  "date": "2024-01-16",\n'
                            '  "type": "consultation_note",\n'
                            '  "...": "...",\n'
                            '  "prescriptions": [\n'
                            '    {\n'
                            '      "medication": "Sertraline",\n'
                            '      "dosage": "75mg",\n'
                            '      "frequency": "once daily",\n'
                            '      "quantity": "30 tablets",\n'
                            '      "refills": 2,\n'
                            '      "pharmacy": "Sunrise Biotech (Lipistal)",\n'
                            '      "supplier": {\n'
                            '        "company": "Sunrise Biotech",\n'
                            '        "brand_name": "Lipistal",\n'
                            '        "price_usd": 4.15,\n'
                            '        "currency": "USD"\n'
                            '      }\n'
                            '    }\n'
                            '  ]\n'
                            '}'
                        ),
                        "Error: medical record not found",
                        "Error: medical record has no prescriptions",
                        "Error: medication Sertraline 50mg not found in record REC999",
                    ],
                },
            },
        }