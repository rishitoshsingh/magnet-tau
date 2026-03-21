from typing import Any, Dict

from tau_bench.envs.telehealth.tools.get_medical_record import (
    GetMedicalRecord as _GetMedicalRecord,
)


class GetMedicalRecord(_GetMedicalRecord):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_medical_record",
                "description": (
                    "Retrieve a patient's medical record by record ID or by the related appointment ID. "
                    "If both record_id and appointment_id are provided, record_id will be used. "
                    "If no matching record is found, an error message is returned."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "record_id": {
                            "type": "string",
                            "description": (
                                "The unique medical record identifier, such as 'REC001'. "
                                "If provided, this is used as the primary lookup key."
                            ),
                        },
                        "appointment_id": {
                            "type": "string",
                            "description": (
                                "The appointment ID associated with the medical record, such as 'APPT002'. "
                                "Used to find the record when record_id is not provided."
                            ),
                        },
                    },
                    "required": [],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "Returns a multi-line, human-readable summary of the medical record if found, including:\n"
                        "- Medical record header with record ID\n"
                        "- Patient and provider names and IDs\n"
                        "- Related appointment (if available): ID, date, and time\n"
                        "- Record date and type\n"
                        "- SOAP-style sections: Subjective, Objective, Assessment, Plan (when present)\n"
                        "- Any recommendations listed as bullet points (when present)\n\n"
                        "If no record_id or appointment_id is provided, returns a guidance message. "
                        "If no matching record is found, returns an error string."
                    ),
                    "examples": [
                        (
                            "Medical Record (ID: REC001)\n"
                            "Patient: David Martinez (ID: david_martinez_5678)\n"
                            "Provider: Dr. Williams Psychiatry (ID: dr_williams_psychiatry)\n"
                            "Related Appointment: APPT002 on 2024-01-16 at 10:00\n"
                            "Date: 2024-01-16\n"
                            "Type: consultation_note\n"
                            "Subjective: Patient reports significant improvement in anxiety symptoms since starting sertraline 6 weeks ago.\n"
                            "Objective: Patient appears calm and engaged. Good eye contact.\n"
                            "Assessment: Generalized anxiety disorder, responding well to sertraline 50mg daily.\n"
                            "Plan: Increase sertraline to 75mg daily and follow up in 6 weeks.\n"
                            "Recommendations:\n"
                            "- Continue medication as adjusted\n"
                            "- Practice daily stress management techniques"
                        ),
                        "Medical record with ID REC999 not found.",
                        "No medical record found for appointment ID APPT999.",
                        "Please provide a record_id or appointment_id to look up the medical record.",
                    ],
                },
            },
        }