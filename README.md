# pymonit

Python server for remote PC monitoring.

## Requirements

Open Hardware Monitor https://openhardwaremonitor.org/ installation is required as pymonit uses its WMI namespace to get sensor information.

`server.py` requires Python WMI wrapper https://pypi.org/project/WMI/.

## Server

`server.py` is a simple httpd that returns CPU and GPU sensor data wrapped in JSON.

```json
[
    {
        "id": "/amdcpu/0",
        "type": "CPU",
        "name": "AMD Ryzen 5 2600X",
        "sensors": [
            {
                "id": "/amdcpu/0/temperature/0",
                "type": "Temperature",
                "name": "CPU Package",
                "value": 37,
                "max": 54.875,
                "min": 31.625
            }
        ]
    },
    {
        "id": "/nvidiagpu/0",
        "type": "GPU",
        "name": "NVIDIA GeForce RTX 2070 SUPER",
        "sensors": [
            {
                "id": "/nvidiagpu/0/temperature/0",
                "type": "Temperature",
                "name": "GPU Core",
                "value": 60,
                "max": 61,
                "min": 28
            }
        ]
    }
]
```