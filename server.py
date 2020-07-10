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
        encoded_data = json.dumps(get_sensor_data()).encode()

        self._set_headers()
        self.wfile.write(encoded_data)


def get_sensor_data():
    import wmi

    temperature_sensors = [
        "/nvidiagpu/0/temperature/0",
        "/amdcpu/0/temperature/0"
    ]
    sensor_data = []

    machine = wmi.WMI(namespace="OpenHardwareMonitor")

    # Temperature sensors
    for sensor in machine.Sensor(SensorType="Temperature"):
        if sensor.Identifier in temperature_sensors:
            sensor_data.append({
                "id": sensor.Identifier,
                "name": sensor.Name,
                "value": sensor.Value,
                "max": sensor.Max,
                "min": sensor.Min
            })

    return sensor_data


def run(server_class=HTTPServer, handler_class=Server, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print("Starting httpd on port %d..." % port)
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
