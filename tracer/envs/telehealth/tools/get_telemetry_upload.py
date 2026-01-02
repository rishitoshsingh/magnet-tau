from typing import Any, Dict

from tau_bench.envs.telehealth.tools.get_telemetry_upload import (
    GetTelemetryUpload as _GetTelemetryUpload,
)


class GetTelemetryUpload(_GetTelemetryUpload):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_telemetry_upload",
                "description": (
                    "Retrieve a specific telemetry upload artifact for a device and date. "
                    "If an upload exists for the given device_id and date, returns a JSON object "
                    "representing the upload record. Otherwise returns an error string."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "Unique identifier of the telemetry device, e.g. 'VC-449'.",
                        },
                        "date": {
                            "type": "string",
                            "description": "The target date in 'YYYY-MM-DD' format.",
                        },
                    },
                    "required": ["device_id", "date"],
                },
                "response": {
                    "oneOf": [
                        {
                            "type": "object",
                            "description": "The telemetry upload record for the given device and date.",
                            "properties": {
                                "device_id": {
                                    "type": "string",
                                    "description": "The device identifier."
                                },
                                "date": {
                                    "type": "string",
                                    "description": "Date of the telemetry upload (YYYY-MM-DD)."
                                },
                                "usage_hours": {
                                    "type": "number",
                                    "description": "Hours of usage recorded for the day."
                                },
                                "synced_at": {
                                    "type": "string",
                                    "description": (
                                        "Timestamp indicating when telemetry was last synced, "
                                        "in ISO 8601 format."
                                    )
                                },
                                "event": {
                                    "type": "string",
                                    "description": (
                                        "Event type associated with the upload, such as 'normal', "
                                        "'error', 'warning', etc."
                                    )
                                },
                                "alerts": {
                                    "type": "array",
                                    "description": "List of alert messages or codes encountered during the day.",
                                    "items": {"type": "string"}
                                },
                            },
                            "required": ["device_id", "date", "usage_hours", "synced_at", "event", "alerts"],
                        },
                        {
                            "type": "string",
                            "description": (
                                "Error message returned when the specified device/date upload was not found."
                            ),
                        },
                    ],
                    "examples": [
                        # Successful example
                        {
                            "device_id": "VC-449",
                            "date": "2025-06-01",
                            "usage_hours": 7.4,
                            "synced_at": "2025-06-01T06:15:00Z",
                            "event": "normal",
                            "alerts": []
                        },
                        {
                            "device_id": "VC-449",
                            "date": "2025-06-02",
                            "usage_hours": 6.8,
                            "synced_at": "2025-06-02T06:12:00Z",
                            "event": "normal",
                            "alerts": []
                        },

                        # Error example
                        "No telemetry upload found for device VC-449 on 2025-06-03."
                    ],
                },
            },
        }