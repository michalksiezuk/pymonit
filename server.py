from http.server import BaseHTTPRequestHandler, HTTPServer
import json


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


def get_temperature_data(sensor):
    return {
        "id": sensor.Identifier,
        "type": "Temperature",
        "name": sensor.Name,
        "value": sensor.Value,
        "max": sensor.Max,
        "min": sensor.Min,
    }


def get_system_info():
    import wmi

    machine = wmi.WMI(namespace="OpenHardwareMonitor")

    cpu_id = "/amdcpu/0"
    gpu_id = "/nvidiagpu/0"

    temperature_sensor_suffix = "/temperature/0"

    return [
        {
            "id": cpu_id,
            "type": "CPU",
            "name": machine.Hardware(Identifier=cpu_id)[0].Name,
            "sensors": [
                get_temperature_data(machine.Sensor(Identifier=cpu_id + temperature_sensor_suffix)[0]),
            ],
        },
        {
            "id": gpu_id,
            "type": "GPU",
            "name": machine.hardware(Identifier=gpu_id)[0].Name,
            "sensors": [
                get_temperature_data(machine.Sensor(Identifier=gpu_id + temperature_sensor_suffix)[0]),
            ],
        },
    ]


def run(server_class=HTTPServer, handler_class=Server, port=8080):
    server_address = ("0.0.0.0", port)
    httpd = server_class(server_address, handler_class)

    print("Starting pymonit server on port %d" % port)
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
