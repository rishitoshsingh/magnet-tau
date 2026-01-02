from typing import Any, Dict

from tau_bench.envs.telehealth.tools.cancel_appointment import (
    CancelAppointment as _CancelAppointment,
)


class CancelAppointment(_CancelAppointment):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "cancel_appointment",
                "description": (
                    "Cancel a scheduled appointment by appointment_id. "
                    "If the appointment is scheduled, its status will be set to 'cancelled', "
                    "with cancellation_reason='patient_cancelled' and cancellation_date set to today. "
                    "If the appointment is already cancelled or completed, an explanatory message is returned instead."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "appointment_id": {
                            "type": "string",
                            "description": "The appointment's unique identifier, such as 'APPT001'.",
                        },
                    },
                    "required": ["appointment_id"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "On success, returns a multi-line human-readable confirmation message containing "
                        "appointment id, patient name, provider name, original date/time, cancellation reason, "
                        "and cancellation date. On failure, returns an error message string explaining why "
                        "the appointment could not be cancelled (not found, already cancelled, or completed)."
                    ),
                    "examples": [
                        # Success example (based on APPT001 + sarah_johnson_1234, provider missing → Unknown Provider)
                        (
                            "Appointment successfully cancelled.\n\n"
                            "Appointment ID: APPT001\n"
                            "Patient: Sarah Johnson\n"
                            "Provider: Dr. Unknown Provider\n"
                            "Original Date/Time: 2024-01-15 at 09:00\n"
                            "Cancellation Reason: Patient Cancelled\n"
                            "Cancellation Date: 2025-01-10\n\n"
                            "The appointment slot is now available for other patients. "
                            "If this was a patient cancellation, please remind them of the cancellation policy."
                        ),

                        # Error: not found
                        "Appointment with ID APPT999 not found.",

                        # Error: already cancelled
                        "Appointment APPT002 is already cancelled.",

                        # Error: already completed
                        "Cannot cancel appointment APPT003 - appointment has already been completed.",
                    ],
                },
            },
        }