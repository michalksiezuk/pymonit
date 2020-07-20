import json
import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Tuple

import wmi


class PymonitServer(BaseHTTPRequestHandler):
    def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer):
        self._machine = wmi.WMI(namespace="OpenHardwareMonitor")

        super().__init__(request, client_address, server)

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        system_info = self._get_system_info()
        encoded_data = json.dumps(system_info).encode()

        self._set_headers()
        self.wfile.write(encoded_data)

    def log_message(self, fmt, *args):
        pass

    def _get_system_info(self):
        hardware = [
            ["CPU", "/amdcpu/0"],
            ["GPU", "/nvidiagpu/0"]
        ]

        return list(map(self._format_hardware_data, hardware))

    def _format_hardware_data(self, hardware):
        temperature_sensor_suffix = "/temperature/0"
        load_sensor_suffix = "/load/0"

        return {
            "id": hardware[1],
            "type": hardware[0],
            "name": self._machine.Hardware(Identifier=hardware[1])[0].Name,
            "sensors": [
                self._format_sensor_data(
                    self._machine.Sensor(Identifier=hardware[1] + temperature_sensor_suffix)[0],
                    "Temperature"
                ),
                self._format_sensor_data(
                    self._machine.Sensor(Identifier=hardware[1] + load_sensor_suffix)[0],
                    "Load"
                )
            ],
        }

    @staticmethod
    def _format_sensor_data(sensor, sensor_type):
        return {
            "id": sensor.Identifier,
            "type": sensor_type,
            "name": sensor.Name,
            "val": sensor.Value,
            "max": sensor.Max,
            "min": sensor.Min,
        }


def run(server_class=HTTPServer, handler_class=PymonitServer, port=8080):
    print(f"Starting pymonit server on port {port}")

    server_address = ("0.0.0.0", port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
