from typing import Any, Dict

from tau_bench.envs.telecom.tools.add_device import AddDevice as _AddDevice


class AddDevice(_AddDevice):
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_device",
                "description": (
                    "Add a device to a customer. The device must be one of the supported device names in the "
                    "device catalog, and the customer must already exist in the system. The device will be "
                    "added to the customer's 'devices' list with a new 'device_id' and 'service' set to null."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": (
                                "The customer's unique identifier, such as 'john_smith_1234'. "
                                "This can be obtained from prior customer lookup tools."
                            ),
                        },
                        "device_name": {
                            "type": "string",
                            "description": "".join(
                                (
                                    "The name of the device to add. Must match one of the known devices in the catalog. ",
                                    "Options: ",
                                    "iPhone 15 Pro, ",
                                    "iPhone 14, ",
                                    "iPhone 13, ",
                                    "Samsung Galaxy S23, ",
                                    "iPhone 12, ",
                                    "iPhone 15, ",
                                    "Google Pixel 8, ",
                                    "Samsung Galaxy A54, ",
                                    "iPhone SE (3rd gen), ",
                                    "WiFi 6 Router, ",
                                    "Standard WiFi Router, ",
                                    "Enterprise Router, ",
                                    "Basic WiFi Router, ",
                                    "Samsung 65\" Smart TV, ",
                                    "HD Cable Box, ",
                                    "55\" Smart TV, ",
                                    "Conference Room TV, ",
                                    "Conference Phone System, ",
                                    "Home Security System."
                                )
                            ),
                        },
                    },
                    "required": ["customer_id", "device_name"],
                },
                "response": {
                    "type": "string",
                    "description": (
                        "A status message indicating whether the device was successfully added. "
                        "On success, it returns a string of the form "
                        "'Success: Added device \"<device_name>\" to customer <customer_id>'. "
                        "On failure, it returns an error string such as "
                        "'Error: Customer not found: <customer_id>' or "
                        "'Error: Invalid device name: <device_name>'."
                    ),
                    "examples": [
                        # Success – using your sample customer
                        "Success: Added device 'iPhone 14' to customer john_smith_1234",
                        # Error – unknown customer
                        "Error: Customer not found: unknown_customer_9999",
                        # Error – invalid device name
                        "Error: Invalid device name: Nokia 3310"
                    ],
                },
            },
        }