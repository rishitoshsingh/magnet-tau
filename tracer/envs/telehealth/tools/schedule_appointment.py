from typing import Any, Dict

from tau_bench.envs.telehealth.tools.schedule_appointment import (
    ScheduleAppointment as _ScheduleAppointment,
)


class ScheduleAppointment(_ScheduleAppointment):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "schedule_appointment",
                "description": (
                    "Schedule a new telehealth appointment for a patient with a healthcare provider.\n\n"
                    "The tool will:\n"
                    "- Validate that the patient and provider exist.\n"
                    "- Validate the appointment date format (YYYY-MM-DD) and derive the weekday.\n"
                    "- Check the provider's weekly schedule to ensure they work on that weekday and "
                    "that the requested time is one of their available time slots.\n"
                    "- Reject the request if the provider is already booked at that date/time with a "
                    "status of 'scheduled' or 'pending_approval'.\n"
                    "- Generate a new appointment ID of the form 'APPT###' based on existing IDs.\n"
                    "- Determine copay based on patient insurance and provider specialty "
                    "(Primary Care vs specialist).\n"
                    "- If bill_insurance=true, mark payment as insurance-based and set copay and "
                    "an insurance authorization code.\n"
                    "- If bill_insurance=false, skip insurance billing, optionally apply a voucher, "
                    "and set payment_method to either 'telehealth_voucher' or 'self_pay'.\n"
                    "- Create a 30-minute scheduled appointment with a telehealth meeting link and "
                    "return a human-readable confirmation summary."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "patient_id": {
                            "type": "string",
                            "description": (
                                "The patient's unique identifier, e.g. 'sarah_johnson_1234'. "
                                "Must exist in the patients dataset."
                            ),
                        },
                        "provider_id": {
                            "type": "string",
                            "description": (
                                "The provider's unique identifier, e.g. 'dr_smith_cardiology'. "
                                "Must exist in the providers dataset."
                            ),
                        },
                        "date": {
                            "type": "string",
                            "description": (
                                "Appointment date in 'YYYY-MM-DD' format. "
                                "The provider's schedule for that weekday will be checked."
                            ),
                        },
                        "time": {
                            "type": "string",
                            "description": (
                                "Appointment time in 'HH:MM' 24-hour format, e.g. '09:00', '15:30'. "
                                "Must exactly match one of the provider's available time slots "
                                "for that weekday."
                            ),
                        },
                        "appointment_type": {
                            "type": "string",
                            "description": (
                                "Type of appointment, such as 'routine_checkup', 'follow_up', "
                                "'consultation', 'specialist_consultation', or 'sick_visit'. "
                                "Stored in the appointment's 'type' field."
                            ),
                        },
                        "bill_insurance": {
                            "type": "boolean",
                            "description": (
                                "Whether to bill the patient's primary insurance for this visit. "
                                "Defaults to true.\n"
                                "- If true: copay is set based on provider specialty "
                                "(primary vs specialist) and an insurance authorization code is generated.\n"
                                "- If false: insurance is not billed, copay is set to 0.0, "
                                "and payment is either via telehealth voucher or self-pay."
                            ),
                            "default": True,
                        },
                        "voucher_id": {
                            "type": "string",
                            "description": (
                                "Optional voucher identifier to apply when bill_insurance is false. "
                                "If provided, payment_method is 'telehealth_voucher'; otherwise 'self_pay'."
                            ),
                        },
                        "payment_notes": {
                            "type": "string",
                            "description": (
                                "Optional free-text notes regarding payment or billing handling. "
                                "Stored in the appointment's 'notes' field if provided."
                            ),
                        },
                    },
                    "required": ["patient_id", "provider_id", "date", "time", "appointment_type"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "On success, returns a multi-line human-readable confirmation message including:\n"
                        "- Appointment ID\n"
                        "- Patient and provider names\n"
                        "- Date, time, and appointment type\n"
                        "- Copay and insurance authorization details (if bill_insurance=true)\n"
                        "- Or voucher/self-pay details (if bill_insurance=false)\n"
                        "- Telehealth meeting link\n"
                        "and a reminder to save the appointment ID.\n\n"
                        "On failure, returns a human-readable error string such as:\n"
                        "- 'Patient with ID ... not found.'\n"
                        "- 'Provider with ID ... not found.'\n"
                        "- 'Invalid date format: ... Please use YYYY-MM-DD format.'\n"
                        "- 'Provider ... does not work on <Day>.'\n"
                        "- 'Provider ... is not available at <time> on <Day>. Available times: ...'\n"
                        "- 'Provider ... already has an appointment scheduled at <time> on <date>.'"
                    ),
                    "examples": [
                        # Success with insurance
                        (
                            "Appointment successfully scheduled!\n\n"
                            "Appointment ID: APPT002\n"
                            "Patient: Sarah Johnson\n"
                            "Provider: Dr. Smith - Cardiology\n"
                            "Date: 2024-01-16\n"
                            "Time: 10:00\n"
                            "Type: Consultation\n"
                            "Copay: $50.00\n"
                            "Insurance Authorization: AUTH000002\n"
                            "Meeting Link: https://telehealth.healthcenter.com/room/APPT002\n\n"
                            "Please save your appointment ID for future reference."
                        ),
                        # Success with voucher / no insurance billing
                        (
                            "Appointment successfully scheduled!\n\n"
                            "Appointment ID: APPT003\n"
                            "Patient: Sarah Johnson\n"
                            "Provider: Dr. Smith - Cardiology\n"
                            "Date: 2024-01-16\n"
                            "Time: 15:00\n"
                            'Type: Follow Up\n'
                            "Insurance Billing: Skipped\n"
                            "Payment Method: Telehealth Voucher\n"
                            "Voucher Applied: VOUCHER123\n"
                            "Amount Due Today: $0.00\n"
                            "Billing Notes: Sponsored follow-up visit\n"
                            "Meeting Link: https://telehealth.healthcenter.com/room/APPT003\n\n"
                            "Please save your appointment ID for future reference."
                        ),
                        # Typical errors
                        "Patient with ID unknown_patient_999 not found.",
                        "Provider with ID dr_unknown not found.",
                        "Invalid date format: 16-01-2024. Please use YYYY-MM-DD format.",
                        "Provider dr_smith_cardiology does not work on Sunday.",
                        (
                            "Provider dr_smith_cardiology is not available at 14:00 on Monday. "
                            "Available times: 09:00, 10:00, 11:00, 15:00, 16:00"
                        ),
                        (
                            "Provider dr_smith_cardiology already has an appointment scheduled "
                            "at 09:00 on 2024-01-15."
                        ),
                    ],
                },
            },
        }