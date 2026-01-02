from typing import Any, Dict

from tau_bench.envs.telehealth.tools.reschedule_appointment import (
    RescheduleAppointment as _RescheduleAppointment,
)


class RescheduleAppointment(_RescheduleAppointment):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "reschedule_appointment",
                "description": (
                    "Reschedule an existing appointment to a new date and time, while enforcing provider "
                    "availability and avoiding double-booking.\n\n"
                    "The tool will:\n"
                    "- Validate that the appointment exists.\n"
                    "- Reject rescheduling for appointments that are already cancelled or completed.\n"
                    "- Look up the provider's weekly schedule and check that the provider works on the "
                    "requested day and that the requested time is one of the available time slots.\n"
                    "- Reject the request if the date format is invalid (must be YYYY-MM-DD).\n"
                    "- Reject the request if another appointment for the same provider already exists at "
                    "the same date and time with status 'scheduled' or 'pending_approval'.\n"
                    "- On success, update the appointment's date and time and return a confirmation summary "
                    "showing the old and new date/time along with patient and provider details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "appointment_id": {
                            "type": "string",
                            "description": (
                                "The appointment's unique identifier to be rescheduled, "
                                "e.g. 'APPT001'."
                            ),
                        },
                        "new_date": {
                            "type": "string",
                            "description": (
                                "New appointment date in 'YYYY-MM-DD' format. "
                                "The provider's workday for this date will be used to check availability "
                                "against their weekly schedule (e.g., Monday, Tuesday)."
                            ),
                        },
                        "new_time": {
                            "type": "string",
                            "description": (
                                "New appointment time in 'HH:MM' 24-hour format, e.g. '09:00', '15:30'. "
                                "Must exactly match one of the provider's available time slots for that day."
                            ),
                        },
                    },
                    "required": ["appointment_id", "new_date", "new_time"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "On success, returns a multi-line human-readable confirmation message, including:\n"
                        "- Appointment ID\n"
                        "- Patient name\n"
                        "- Provider name and specialty\n"
                        "- Previous date/time\n"
                        "- New date/time\n"
                        "- Meeting link\n\n"
                        "On failure, returns a human-readable error string explaining why the reschedule "
                        "could not be performed, such as:\n"
                        "- Appointment not found\n"
                        "- Appointment already cancelled or completed\n"
                        "- Invalid date format\n"
                        "- Provider does not work that day\n"
                        "- Provider is not available at the requested time\n"
                        "- Provider already has a conflicting appointment at that slot."
                    ),
                    "examples": [
                        # Example success
                        (
                            "Appointment successfully rescheduled.\n\n"
                            "Appointment ID: APPT001\n"
                            "Patient: Sarah Johnson\n"
                            "Provider: Dr. Garcia - Primary Care\n\n"
                            "Previous Date/Time: 2024-01-15 at 09:00\n"
                            "New Date/Time: 2024-01-16 at 10:00\n\n"
                            "Meeting Link: https://telehealth.healthcenter.com/room/APPT001\n\n"
                            "Please update your calendar with the new appointment time."
                        ),
                        # Appointment not found
                        "Appointment with ID APPT999 not found.",
                        # Cancelled / completed
                        "Cannot reschedule appointment APPT010 - appointment has been cancelled.",
                        "Cannot reschedule appointment APPT011 - appointment has already been completed.",
                        # Invalid date
                        "Invalid date format: 15-01-2024. Please use YYYY-MM-DD format.",
                        # Provider not working that day
                        "Provider dr_smith_cardiology does not work on Sunday.",
                        # Provider unavailable at that time
                        (
                            "Provider dr_smith_cardiology is not available at 13:00 on Monday. "
                            "Available times: 09:00, 10:00, 11:00, 15:00, 16:00"
                        ),
                        # Double-booking
                        (
                            "Provider dr_smith_cardiology already has an appointment scheduled at "
                            "09:00 on 2024-01-15."
                        ),
                    ],
                },
            },
        } 