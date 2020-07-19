import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        encoded_data = json.dumps(get_system_info()).encode()

        self._set_headers()
        self.wfile.write(encoded_data)

    def log_message(self, fmt, *args):
        pass


def format_sensor_data(sensor, sensor_type):
    return {
        "id": sensor.Identifier,
        "type": sensor_type,
        "name": sensor.Name,
        "val": sensor.Value,
        "max": sensor.Max,
        "min": sensor.Min,
    }


def get_system_info():
    import wmi

    machine = wmi.WMI(namespace="OpenHardwareMonitor")

    cpu_id = "/amdcpu/0"
    gpu_id = "/nvidiagpu/0"

    temperature_sensor_suffix = "/temperature/0"
    load_sensor_suffix = "/load/0"

    return [
        {
            "id": cpu_id,
            "type": "CPU",
            "name": machine.Hardware(Identifier=cpu_id)[0].Name,
            "sensors": [
                format_sensor_data(
                    machine.Sensor(Identifier=cpu_id + temperature_sensor_suffix)[0],
                    "Temperature"
                ),
                format_sensor_data(
                    machine.Sensor(Identifier=cpu_id + load_sensor_suffix)[0],
                    "Load"
                )
            ],
        },
        {
            "id": gpu_id,
            "type": "GPU",
            "name": machine.hardware(Identifier=gpu_id)[0].Name,
            "sensors": [
                format_sensor_data(
                    machine.Sensor(Identifier=gpu_id + temperature_sensor_suffix)[0],
                    "Temperature"
                ),
                format_sensor_data(
                    machine.Sensor(Identifier=gpu_id + load_sensor_suffix)[0],
                    "Load"
                )
            ],
        },
    ]


def run(server_class=HTTPServer, handler_class=Server, port=8080):
    server_address = ("0.0.0.0", port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting pymonit server on port {port}")
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
