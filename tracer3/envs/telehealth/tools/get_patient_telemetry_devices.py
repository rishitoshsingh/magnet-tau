import json
from typing import Any, Dict, List

from tau_bench.envs.tool import Tool


class GetPatientTelemetryDevices(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], patient_id: str) -> str:
        patients = data.get("patients", {})
        if patient_id not in patients:
            return f"Patient with ID {patient_id} not found."

        inventory: List[Dict[str, Any]] = data.get("telemetry_inventory", [])
        assigned_devices = [
            dict(device)
            for device in inventory
            if device.get("assigned_to") == patient_id
        ]
        if not assigned_devices:
            return f"No telemetry devices assigned to patient {patient_id}."

        uploads: List[Dict[str, Any]] = data.get("telemetry_uploads", [])
        results: List[Dict[str, Any]] = []
        for device in sorted(assigned_devices, key=lambda item: item.get("device_id", "")):
            device_id = device.get("device_id")
            device_uploads = sorted(
                [dict(upload) for upload in uploads if upload.get("device_id") == device_id],
                key=lambda item: item.get("date", ""),
            )
            device_details = dict(device)
            device_details["telemetry_uploads"] = device_uploads
            device_details["latest_upload"] = device_uploads[-1] if device_uploads else None
            results.append(device_details)

        return json.dumps(results, indent=2)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_patient_telemetry_devices",
                "description": (
                    "Return the complete telemetry device details assigned to a patient, "
                    "including device inventory fields and any telemetry uploads for each device."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "patient_id": {
                            "type": "string",
                            "description": (
                                "The patient's unique identifier, such as "
                                "'avery_morgan_tracer_0001'."
                            ),
                        }
                    },
                    "required": ["patient_id"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "On success, returns a JSON-encoded array of assigned telemetry devices. "
                        "Each entry includes the full inventory record, a 'telemetry_uploads' array, "
                        "and a 'latest_upload' object when uploads exist. On failure, returns an "
                        "informative error string."
                    ),
                    "examples": [
                        (
                            "[\n"
                            "  {\n"
                            '    "device_id": "CARDIA_tracer_451",\n'
                            '    "device_type": "Cardiac Event Monitor",\n'
                            '    "status": "deployed",\n'
                            '    "last_audit": "2026-01-10",\n'
                            '    "assigned_to": "avery_morgan_tracer_0001",\n'
                            '    "notes": "Assigned to avery_morgan_tracer_0001 for rhythm_surveillance",\n'
                            '    "telemetry_uploads": [\n'
                            "      {\n"
                            '        "device_id": "CARDIA_tracer_451",\n'
                            '        "date": "2025-11-25",\n'
                            '        "usage_hours": 6.8,\n'
                            '        "synced_at": "2025-11-25T06:15:00Z",\n'
                            '        "event": "normal",\n'
                            '        "alerts": []\n'
                            "      }\n"
                            "    ],\n"
                            '    "latest_upload": {\n'
                            '      "device_id": "CARDIA_tracer_451",\n'
                            '      "date": "2025-12-01",\n'
                            '      "usage_hours": 7.0,\n'
                            '      "synced_at": "2025-12-01T06:15:00Z",\n'
                            '      "event": "normal",\n'
                            '      "alerts": []\n'
                            "    }\n"
                            "  }\n"
                            "]"
                        ),
                        "No telemetry devices assigned to patient patient_without_device_0001.",
                        "Patient with ID unknown_patient_9999 not found.",
                    ],
                },
            },
        }
