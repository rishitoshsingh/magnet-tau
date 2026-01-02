
from typing import Any, Dict

from tau_bench.envs.telehealth.tools.get_appointment_details import (
    GetAppointmentDetails as _GetAppointmentDetails,
)


class GetAppointmentDetails(_GetAppointmentDetails):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_appointment_details",
                "description": (
                    "Get detailed information about a scheduled appointment, including patient, provider, "
                    "date, time, clinical details, billing information, and any prescription, referral, "
                    "or cancellation details if present."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "appointment_id": {
                            "type": "string",
                            "description": (
                                "The appointment's unique identifier, such as 'APPT001'. "
                                "This must match an existing appointment_id in the environment data."
                            ),
                        },
                    },
                    "required": ["appointment_id"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "Returns a human-readable, multi-line text summary of the appointment. "
                        "If the appointment exists, the output includes:\n"
                        "- Header with appointment ID\n"
                        "- Patient and provider information\n"
                        "- Appointment details (date, time, duration, type, status)\n"
                        "- Clinical information (chief complaint, notes)\n"
                        "- Billing information (insurance authorization, copay amount)\n"
                        "- Meeting information (telehealth link)\n"
                        "- Optional sections for prescription, referral, and cancellation details if those fields exist.\n"
                        "If the appointment is not found, returns an error message like "
                        "'Appointment with ID APPT001 not found.'"
                    ),
                    "examples": [
                        (
                            "Appointment Details (ID: APPT001)\n\n"
                            "Patient: Sarah Johnson (ID: sarah_johnson_1234)\n"
                            "Provider: Dr. Garcia - Primary Care (ID: dr_garcia_primary)\n\n"
                            "Appointment Information:\n"
                            "- Date: 2024-01-15\n"
                            "- Time: 09:00\n"
                            "- Duration: 30 minutes\n"
                            "- Type: Routine Checkup\n"
                            "- Status: Scheduled\n\n"
                            "Clinical Information:\n"
                            "- Chief Complaint: Annual physical examination\n"
                            "- Notes: Patient requesting routine physical, blood pressure check\n\n"
                            "Billing Information:\n"
                            "- Insurance Authorization: AUTH123456\n"
                            "- Copay Amount: $25.00\n\n"
                            "Meeting Information:\n"
                            "- Meeting Link: https://telehealth.healthcenter.com/room/APPT001"
                        ),
                        (
                            "Appointment Details (ID: APPT010)\n\n"
                            "Patient: Sarah Johnson (ID: sarah_johnson_1234)\n"
                            "Provider: Dr. Smith - Cardiology (ID: dr_smith_cardiology)\n\n"
                            "Appointment Information:\n"
                            "- Date: 2024-02-10\n"
                            "- Time: 14:30\n"
                            "- Duration: 45 minutes\n"
                            "- Type: Follow Up\n"
                            "- Status: Completed\n\n"
                            "Clinical Information:\n"
                            "- Chief Complaint: Follow-up for hypertension management\n"
                            "- Notes: Blood pressure improved, continue current regimen\n\n"
                            "Billing Information:\n"
                            "- Insurance Authorization: AUTH987654\n"
                            "- Copay Amount: $30.00\n\n"
                            "Meeting Information:\n"
                            "- Meeting Link: https://telehealth.healthcenter.com/room/APPT010\n\n"
                            "Prescription Issued:\n"
                            "- Lisinopril 10mg once daily\n"
                            "- Quantity: 90, Refills: 3"
                        ),
                        "Appointment with ID APPT999 not found.",
                    ],
                },
            },
        }