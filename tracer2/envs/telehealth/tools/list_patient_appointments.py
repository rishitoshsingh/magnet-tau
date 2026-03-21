from typing import Any, Dict

from tau_bench.envs.telehealth.tools.list_patient_appointments import (
    ListPatientAppointments as _ListPatientAppointments,
)


class ListPatientAppointments(_ListPatientAppointments):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_patient_appointments",
                "description": (
                    "List all appointments for a patient, optionally filtering by an "
                    "appointment status such as 'scheduled', 'pending_approval', or 'cancelled'. "
                    "Results are sorted chronologically by date and time and include provider name, "
                    "specialty, status, and appointment type in a human-readable format."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "patient_id": {
                            "type": "string",
                            "description": (
                                "The patient's unique identifier, such as 'sarah_johnson_1234'. "
                                "Must exist in the patients dataset."
                            ),
                        },
                        "status_filter": {
                            "type": "string",
                            "description": (
                                "Optional appointment status filter (case-insensitive). "
                                "Examples: 'scheduled', 'completed', 'cancelled', 'pending_approval'. "
                                "If omitted, all appointments for the patient are listed."
                            ),
                        },
                    },
                    "required": ["patient_id"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "A multi-line, human-readable string listing the patient's appointments "
                        "chronologically. Each line includes appointment ID, date, time, provider "
                        "name and specialty, status, and appointment type. If no matching "
                        "appointments are found, or if the patient ID is invalid, an informative "
                        "error-style message string is returned instead."
                    ),
                    "examples": [
                        # Successful listing for Sarah with one scheduled appointment
                        (
                            "Appointments for Sarah Johnson (ID: sarah_johnson_1234)\n"
                            "- APPT001: 2024-01-15 at 09:00 with Dr. Garcia (Primary Care) "
                            "[Scheduled, Type: Routine Checkup]"
                        ),
                        # Filtered with no matches
                        (
                            "No appointments found for patient sarah_johnson_1234 with status cancelled."
                        ),
                        # No appointments at all for a valid patient
                        (
                            "No appointments found for patient david_martinez_5678."
                        ),
                        # Invalid patient ID
                        (
                            "Patient with ID unknown_patient_9999 not found."
                        ),
                    ],
                },
            },
        }