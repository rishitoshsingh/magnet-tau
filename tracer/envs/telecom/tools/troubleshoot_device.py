from typing import Any, Dict

from tau_bench.envs.telecom.tools.troubleshoot_device import (
    TroubleshootDevice as _TroubleshootDevice,
)


class TroubleshootDevice(_TroubleshootDevice):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "troubleshoot_device",
                "description": (
                    "Provide troubleshooting steps for a given device and issue type. "
                    "If the device is not found or the issue is not recognized for the device category, "
                    "an error string or 'Unknown issue' is returned."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_name": {
                            "type": "string",
                            "description": (
                                "Name of the device, such as 'iPhone 15 Pro' or 'WiFi 6 Router'. "
                                "Must exist in the device catalog."
                            ),
                        },
                        "issue": {
                            "type": "string",
                            "enum": ["no_service", "slow_speeds", "battery_drain"],
                            "description": (
                                "Issue type to troubleshoot. Supported issues: "
                                "'no_service', 'slow_speeds', 'battery_drain'."
                            ),
                        },
                    },
                    "required": ["device_name", "issue"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "Returns troubleshooting steps as a multi-line string. "
                        "If the device is not found, returns an error string "
                        "'Error: Device not found: <device_name>'. "
                        "If the issue is unsupported for the device category, returns 'Unknown issue'."
                    ),
                    "examples": [
                        # Success (mobile phone battery issue)
                        (
                            "Troubleshooting steps: \n"
                            "1) Restart device \n"
                            "2) Check brightness settings and reduce if needed\n"
                            "3) Close background apps\n"
                            "4) Contact support if issue persists\n"
                        ),
                        
                        # Success (mobile phone no service)
                        (
                            "Troubleshooting steps: \n"
                            "1) Restart device \n"
                            "2) Check signal coverage \n"
                            "3) Reset network settings \n"
                            "4) Contact support if issue persists\n"
                        ),

                        # Error (device not in dataset)
                        "Error: Device not found: Nokia 3310",

                        # Error (unknown / unsupported issue)
                        "Unknown issue"
                    ],
                },
            },
        }