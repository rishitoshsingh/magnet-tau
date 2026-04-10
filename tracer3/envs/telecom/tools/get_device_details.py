from typing import Any, Dict

from tau_bench.envs.telecom.tools.get_device_details import (
    GetDeviceDetails as _GetDeviceDetails,
)


class GetDeviceDetails(_GetDeviceDetails):

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_device_details",
                "description": (
                    "Get detailed information about a device available in the catalog. "
                    "Returns device metadata such as category, manufacturer, and model. "
                    "If the device name is not found, an error string is returned."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_name": {
                            "type": "string",
                            "description": "".join(
                                (
                                    "The name of the device to get details about.",
                                    "Options: ",
                                    "iPhone 15 Pro",
                                    "iPhone 14",
                                    "iPhone 13",
                                    "Samsung Galaxy S23",
                                    "iPhone 12",
                                    "iPhone 15",
                                    "Google Pixel 8",
                                    "Samsung Galaxy A54",
                                    "iPhone SE (3rd gen)",
                                    "WiFi 6 Router",
                                    "Standard WiFi Router",
                                    "Enterprise Router",
                                    "Basic WiFi Router",
                                    "Samsung 65\" Smart TV",
                                    "HD Cable Box",
                                    "55\" Smart TV",
                                    "Conference Room TV",
                                    "Conference Phone System",
                                    "Home Security System",
                                )
                            ),
                        },
                    },
                    "required": ["device_name"],
                },
                "response": {
                    "type": "object",
                    "description": (
                        "The device details object for the requested device, including category, "
                        "manufacturer, and model. If the device does not exist in the catalog, "
                        "the function returns the string 'Error: Device not found: <device_name>'."
                    ),
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Device category, such as 'mobile_phone' or 'router'."
                        },
                        "manufacturer": {
                            "type": "string",
                            "description": "Name of the manufacturer, such as 'Apple' or 'Samsung'."
                        },
                        "model": {
                            "type": "string",
                            "description": "Device model name."
                        },
                    },
                    "required": ["category", "manufacturer", "model"],
                    "examples": [
                        # Sample valid devices
                        {
                            "category": "mobile_phone",
                            "manufacturer": "Apple",
                            "model": "iPhone 15 Pro"
                        },
                        {
                            "category": "mobile_phone",
                            "manufacturer": "Samsung",
                            "model": "Galaxy S23"
                        },
                        # Error case
                        "Error: Device not found: Motorola Razr 2025"
                    ],
                },
            },
        }