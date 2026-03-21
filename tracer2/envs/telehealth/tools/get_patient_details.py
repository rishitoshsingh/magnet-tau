from typing import Any, Dict

from tau_bench.envs.telehealth.tools.get_patient_details import (
    GetPatientDetails as _GetPatientDetails,
)


class GetPatientDetails(_GetPatientDetails):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_patient_details",
                "description": (
                    "Retrieve detailed information about a patient including demographics, address, "
                    "insurance information, medical history, current medications, and emergency contact. "
                    "Returns a formatted multi-line string. If the patient is not found, returns an "
                    "error message string."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "patient_id": {
                            "type": "string",
                            "description": "The patient's unique identifier, such as 'sarah_johnson_1234'.",
                        },
                    },
                    "required": ["patient_id"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "Human-readable multi-line patient summary, or an error message. "
                        "The result includes:\n"
                        "- Name and ID\n"
                        "- Demographics\n"
                        "- Address\n"
                        "- Insurance details\n"
                        "- Medical history (conditions, allergies, medications)\n"
                        "- Emergency contact information"
                    ),
                    "examples": [
                        (
                            "Patient Details for Sarah Johnson (ID: sarah_johnson_1234)\n\n"
                            "Demographics:\n"
                            "- Date of Birth: 1985-03-15\n"
                            "- Gender: Female\n"
                            "- Phone: (555) 123-4567\n"
                            "- Email: sarah.johnson@email.com\n\n"
                            "Address:\n"
                            "- 123 Maple Street\n"
                            "- Apt 2B\n"
                            "- Boston, MA 02101\n"
                            "- USA\n\n"
                            "Insurance:\n"
                            "- Provider: Blue Cross Blue Shield\n"
                            "- Policy Number: BCBS123456789\n"
                            "- Primary Care Copay: $25.00\n"
                            "- Specialist Copay: $50.00\n\n"
                            "Medical History:\n"
                            "- Conditions: Hypertension, Type 2 Diabetes\n"
                            "- Allergies: Penicillin, Shellfish\n"
                            "- Current Medications: Metformin 500mg twice daily, Lisinopril 10mg once daily\n\n"
                            "Emergency Contact:\n"
                            "- Michael Johnson (Spouse)\n"
                            "- Phone: (555) 123-4568"
                        ),
                        (
                            "Patient Details for David Martinez (ID: david_martinez_5678)\n\n"
                            "Demographics:\n"
                            "- Date of Birth: 1978-11-22\n"
                            "- Gender: Male\n"
                            "- Phone: (555) 234-5678\n"
                            "- Email: david.martinez@email.com\n\n"
                            "Address:\n"
                            "- 456 Oak Avenue\n"
                            "- \n"
                            "- Los Angeles, CA 90210\n"
                            "- USA\n\n"
                            "Insurance:\n"
                            "- Provider: Aetna\n"
                            "- Policy Number: AET987654321\n"
                            "- Primary Care Copay: $30.00\n"
                            "- Specialist Copay: $60.00\n\n"
                            "Medical History:\n"
                            "- Conditions: Anxiety, Seasonal Allergies\n"
                            "- Allergies: Latex\n"
                            "- Current Medications: Sertraline 50mg once daily, Claritin 10mg as needed\n\n"
                            "Emergency Contact:\n"
                            "- Maria Martinez (Sister)\n"
                            "- Phone: (555) 234-5679"
                        ),
                        # Error case:
                        "Patient with ID unknown_patient_0000 not found."
                    ],
                },
            },
        }