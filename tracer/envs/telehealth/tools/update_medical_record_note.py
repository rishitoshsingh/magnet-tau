from typing import Any, Dict

from tau_bench.envs.telehealth.tools.update_medical_record_note import (
    UpdateMedicalRecordNote as _UpdateMedicalRecordNote,
)


class UpdateMedicalRecordNote(_UpdateMedicalRecordNote):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_medical_record_note",
                "description": (
                    "Append an audit or compliance note to an existing medical record.\n\n"
                    "Behavior:\n"
                    "- Looks up the medical record by record_id in data['medical_records'].\n"
                    "- If the record does not exist, returns an error string "
                    "like 'Error: medical record REC999 not found'.\n"
                    "- Ensures the record has a 'notes' list (creates it if missing).\n"
                    "- Appends a new entry of the form {'note': <note>, 'metadata': <metadata?>}.\n"
                    "- Returns the full updated medical record as a JSON string."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "record_id": {
                            "type": "string",
                            "description": (
                                "Identifier of the medical record to update, e.g. 'REC001'. "
                                "Must exist in data['medical_records'] or an error string is returned."
                            ),
                        },
                        "note": {
                            "type": "string",
                            "description": (
                                "Free-text note to append to the record's 'notes' list. "
                                "Use this for audit trail entries, compliance annotations, "
                                "clarifications, or follow-up instructions."
                            ),
                        },
                        "metadata": {
                            "type": "object",
                            "description": (
                                "Optional structured metadata to attach alongside the note. "
                                "Common fields might include 'author', 'timestamp', 'role', "
                                "'reason_code', or 'source_system'. If provided, it is stored "
                                "under the 'metadata' key in the appended note entry."
                            ),
                        },
                    },
                    "required": ["record_id", "note"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "On success: JSON string of the full updated medical record, including the "
                        "newly appended note entry in the 'notes' array.\n"
                        "On failure: error string 'Error: medical record <record_id> not found'."
                    ),
                    "examples": [
                        # Success example (shape only, not full record)
                        (
                            '{\n'
                            '  "record_id": "REC001",\n'
                            '  "appointment_id": "APPT002",\n'
                            '  "patient_id": "david_martinez_5678",\n'
                            '  "provider_id": "dr_williams_psychiatry",\n'
                            '  "date": "2024-01-16",\n'
                            '  "type": "consultation_note",\n'
                            '  "...": "...",\n'
                            '  "notes": [\n'
                            '    {"note": "QA review completed",\n'
                            '     "metadata": {"author": "compliance_bot", "timestamp": "2024-02-01T10:15:00Z"}}\n'
                            '  ]\n'
                            '}'
                        ),
                        "Error: medical record REC999 not found",
                    ],
                },
            },
        }