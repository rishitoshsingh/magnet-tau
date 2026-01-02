from typing import Any, Dict

from tau_bench.envs.telehealth.tools.list_telemetry_devices import (
    ListTelemetryDevices as _ListTelemetryDevices,
)


class ListTelemetryDevices(_ListTelemetryDevices):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_telemetry_devices",
                "description": (
                    "List telemetry wearable devices from the telemetry inventory, optionally "
                    "filtered by device status and limited to a maximum number of entries. "
                    "Devices are sorted by device_id in ascending order before limiting."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status_filter": {
                            "type": "string",
                            "description": (
                                "Optional status filter to restrict results. Comparison is "
                                "case-insensitive. Examples: 'available', 'shipped', "
                                "'missing_overdue'. If omitted, all devices are listed."
                            ),
                        },
                        "limit": {
                            "type": "integer",
                            "description": (
                                "Optional maximum number of devices to list. If provided and > 0, "
                                "only the first N devices (after sorting) are included."
                            ),
                        },
                    },
                    "required": [],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "A human-readable string. In the normal case it begins with the header "
                        "'Telemetry devices:' followed by one line per device in the format:\n\n"
                        "  <device_id> | status=<status> | last_audit=<YYYY-MM-DD> | notes=<free text>\n\n"
                        "If the telemetry inventory is empty, returns:\n"
                        "  'Telemetry inventory is empty.'\n\n"
                        "If a status_filter is provided but no devices match, returns:\n"
                        "  'No telemetry devices with status <status_filter>.'"
                    ),
                    "examples": [
                        # Full list (using your sample data)
                        (
                            "Telemetry devices:\n"
                            "NS-EEG-218 | status=available | last_audit=2025-07-20 | notes=Spare unit ready for dispatch\n"
                            "NS-EEG-219 | status=shipped | last_audit=2025-07-18 | notes=In transit to patient\n"
                            "NS-EEG-220 | status=missing_overdue | last_audit=2025-07-05 | notes=Flagged missing; escalate replacement"
                        ),
                        # Filtered by status
                        (
                            "Telemetry devices:\n"
                            "NS-EEG-218 | status=available | last_audit=2025-07-20 | notes=Spare unit ready for dispatch"
                        ),
                        # No matches for filter
                        "No telemetry devices with status retired.",
                        # Empty inventory
                        "Telemetry inventory is empty.",
                    ],
                },
            },
        }
