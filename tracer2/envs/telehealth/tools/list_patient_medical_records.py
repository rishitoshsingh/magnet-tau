from __future__ import annotations

from typing import Any, Dict

from tau_bench.envs.telehealth.tools.list_patient_medical_records import (
    ListPatientMedicalRecords as _ListPatientMedicalRecords,
)


class ListPatientMedicalRecords(_ListPatientMedicalRecords):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_patient_medical_records",
                "description": (
                    "List a patient's medical records (most recent first). Each record line includes "
                    "record_id, date, related appointment_id, and a comma-separated list of prescribed medications "
                    "if present. Supports an optional 'limit' to restrict how many records are returned."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "patient_id": {
                            "type": "string",
                            "description": (
                                "ID of the patient, such as 'david_martinez_5678'. Must exist in the "
                                "medical_records dataset, otherwise an error-style string is returned."
                            ),
                        },
                        "limit": {
                            "type": "integer",
                            "description": (
                                "Optional maximum number of records to return. If provided and > 0, "
                                "only the newest N records are included."
                            ),
                        },
                    },
                    "required": ["patient_id"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "A multi-line, human-readable string. The first line is a header "
                        "('Medical records (newest first):'), followed by one line per record in the format:\n"
                        "record_id=<ID> | date=<YYYY-MM-DD> | appointment_id=<APPT_ID> | medications=<list or 'None recorded'>.\n"
                        "If no records are found for the patient, an informative message is returned instead."
                    ),
                    "examples": [
                        # Successful listing with one record (your sample REC001)
                        (
                            "Medical records (newest first):\n"
                            "record_id=REC001 | date=2024-01-16 | appointment_id=APPT002 | "
                            "medications=Sertraline"
                        ),
                        # No records for this patient
                        "No medical records found for patient sarah_johnson_1234.",
                        # Multiple records with a limit applied
                        (
                            "Medical records (newest first):\n"
                            "record_id=REC010 | date=2024-05-10 | appointment_id=APPT020 | "
                            "medications=Metformin, Lisinopril\n"
                            "record_id=REC007 | date=2024-03-01 | appointment_id=APPT015 | "
                            "medications=None recorded"
                        ),
                    ],
                },
            },
        }