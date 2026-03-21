from typing import Any, Dict

from tau_bench.envs.telehealth.tools.list_telemetry_uploads import (
    ListTelemetryUploads as _ListTelemetryUploads,
)


class ListTelemetryUploads(_ListTelemetryUploads):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_telemetry_uploads",
                "description": (
                    "List telemetry upload artifacts for a given device over an optional "
                    "date window. Entries are filtered by device_id, optionally constrained "
                    "to start_date/end_date (inclusive), then sorted by date in ascending "
                    "order before applying any limit."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": (
                                "Unique identifier of the telemetry device, e.g. 'VC-449'. "
                                "This is required."
                            ),
                        },
                        "start_date": {
                            "type": "string",
                            "description": (
                                "Optional inclusive start date in 'YYYY-MM-DD' format. "
                                "If provided, only uploads on or after this date are returned."
                            ),
                        },
                        "end_date": {
                            "type": "string",
                            "description": (
                                "Optional inclusive end date in 'YYYY-MM-DD' format. "
                                "If provided, only uploads on or before this date are returned."
                            ),
                        },
                        "limit": {
                            "type": "integer",
                            "description": (
                                "Optional maximum number of entries to return. "
                                "If provided and > 0, only the first N entries (after sorting "
                                "by date ascending) are included."
                            ),
                        },
                    },
                    "required": ["device_id"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "On success: a JSON-encoded array of telemetry upload objects for "
                        "the requested device, already filtered and sorted by date ascending. "
                        "Each object typically includes fields such as:\n\n"
                        "  {\n"
                        "    \"device_id\": \"VC-449\",\n"
                        "    \"date\": \"2025-06-01\",\n"
                        "    \"usage_hours\": 7.4,\n"
                        "    \"synced_at\": \"2025-06-01T06:15:00Z\",\n"
                        "    \"event\": \"normal\",\n"
                        "    \"alerts\": []\n"
                        "  }\n\n"
                        "If no uploads match the device_id and date window, returns a human-"
                        "readable message instead:\n"
                        "  'No telemetry uploads found for device <device_id> in the specified window.'"
                    ),
                    "examples": [
                        # Full range for the sample device
                        (
                            "[\n"
                            "  {\n"
                            "    \"device_id\": \"VC-449\",\n"
                            "    \"date\": \"2025-06-01\",\n"
                            "    \"usage_hours\": 7.4,\n"
                            "    \"synced_at\": \"2025-06-01T06:15:00Z\",\n"
                            "    \"event\": \"normal\",\n"
                            "    \"alerts\": []\n"
                            "  },\n"
                            "  {\n"
                            "    \"device_id\": \"VC-449\",\n"
                            "    \"date\": \"2025-06-02\",\n"
                            "    \"usage_hours\": 6.8,\n"
                            "    \"synced_at\": \"2025-06-02T06:12:00Z\",\n"
                            "    \"event\": \"normal\",\n"
                            "    \"alerts\": []\n"
                            "  },\n"
                            "  {\n"
                            "    \"device_id\": \"VC-449\",\n"
                            "    \"date\": \"2025-06-03\",\n"
                            "    \"usage_hours\": 5.9,\n"
                            "    \"synced_at\": \"2025-06-03T06:09:00Z\",\n"
                            "    \"event\": \"normal\",\n"
                            "    \"alerts\": []\n"
                            "  }\n"
                            "]"
                        ),
                        # With date window and limit
                        (
                            "[\n"
                            "  {\n"
                            "    \"device_id\": \"VC-449\",\n"
                            "    \"date\": \"2025-06-02\",\n"
                            "    \"usage_hours\": 6.8,\n"
                            "    \"synced_at\": \"2025-06-02T06:12:00Z\",\n"
                            "    \"event\": \"normal\",\n"
                            "    \"alerts\": []\n"
                            "  }\n"
                            "]"
                        ),
                        # No results in window
                        "No telemetry uploads found for device VC-449 in the specified window."
                    ],
                },
            },
        }