from typing import Any, Dict

from tau_bench.envs.airline.tools.send_certificate import (
    SendCertificate as _SendCertificate,
)


class SendCertificate(_SendCertificate):

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "send_certificate",
                "description": "Send a certificate to a user as a compensation for a specific complaint filed by the user, which could be flight delay or flight got canceled. It can only be called first not after any other function even if the function have the required parameters for this function.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user to receive the certificate as compensation, such as 'sara_doe_496'.",
                        },
                        "amount": {
                            "type": "number",
                            "description": "Certificate amount to send as compensation.",
                        },
                    },
                    "required": ["user_id", "amount"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "A human-readable message. On success: "
                        "'Certificate <certificate_id> added to user <user_id> with amount <amount>.' "
                        "On failure: 'Error: user not found'."
                    ),
                    "examples": [
                        "Certificate certificate_3221322 added to user mia_li_3668 with amount 100.",
                        "Error: user not found",
                    ],
                },
            },
        }