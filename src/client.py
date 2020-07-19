import asyncio
from sys import exit

import aiohttp
from asciimatics.effects import Print
from asciimatics.exceptions import ResizeScreenError
from asciimatics.renderers import FigletText, Rainbow
from asciimatics.scene import Scene
from asciimatics.screen import Screen

PYMONIT_ENDPOINT = "http://192.168.0.100:8080"


class Endpoint:
    def __init__(self):
        self._loop = asyncio.get_event_loop()

    @staticmethod
    async def _async_get():
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(PYMONIT_ENDPOINT) as response:
                    return await response.json()
            except aiohttp.ClientConnectorError as error:
                print('Connection Error', str(error))

    def get(self):
        return self._loop.run_until_complete(self._async_get())


class PymonitScene(Scene):
    def __init__(self, screen):
        self._screen = screen
        self._endpoint = Endpoint()
        self._vitals = self._endpoint.get()
        self._effects = [
            Print(
                screen,
                Rainbow(
                    screen,
                    FigletText("pymonit", font="poison"),
                ),
                screen.height // 2 - 14,
                speed=1
            )
        ]

        super(PymonitScene, self).__init__(self._effects, 20, clear=False)

    def render_system_info(self):
        if len(self._vitals) != 0:
            cpu = self._vitals[0]
            gpu = self._vitals[1]

            self._screen.print_at(
                "> SYSTEM COMPONENTS --------------------------------------------",
                self._screen.width // 2 - 33,
                self._screen.height // 2 - 1
            )

            self._screen.print_at(
                f"CPU: {cpu['name']}",
                self._screen.width // 2 - 33,
                self._screen.height // 2 + 1
            )

            self._screen.print_at(
                f"GPU: {gpu['name']}",
                self._screen.width // 2 - 33,
                self._screen.height // 2 + 2
            )

    def render_vitals(self):
        self._screen.print_at(
            "> VITALS -------------------------------------------------------",
            self._screen.width // 2 - 33,
            self._screen.height // 2 + 5
        )

        self._screen.print_at(
            "CPU TEMP:",
            self._screen.width // 2 - 33,
            self._screen.height // 2 + 7
        )

        self._screen.print_at(
            "CPU LOAD:",
            self._screen.width // 2 - 33,
            self._screen.height // 2 + 11
        )

        self._screen.print_at(
            "GPU TEMP:",
            self._screen.width // 2 + 4,
            self._screen.height // 2 + 7
        )

        self._screen.print_at(
            "GPU LOAD:",
            self._screen.width // 2 + 4,
            self._screen.height // 2 + 11
        )

    @staticmethod
    def _format_load_string(self, sensor):
        load_current = round(sensor["val"], 2)
        load_min = round(sensor["min"], 2)
        load_max = round(sensor["max"], 2)

        return f"{load_current}/{load_min}/{load_max}   "

    def render_sensor_value(self):
        cpu_temp = cpu_load = gpu_temp = gpu_load = ""
        half_width = self._screen.width // 2
        half_height = self._screen.height // 2

        if len(self._vitals) != 0:
            cpu = self._vitals[0]
            cpu_temp = str(round(cpu["sensors"][0]["val"]))
            cpu_load = self._format_load_string(self, cpu["sensors"][1])

            gpu = self._vitals[1]
            gpu_temp = str(round(gpu["sensors"][0]["val"]))
            gpu_load = self._format_load_string(self, gpu["sensors"][1])

        cpu_figure = FigletText(f"{cpu_temp}", font="small")
        gpu_figure = FigletText(f"{gpu_temp}", font="small")

        # CPU temperature
        self._effects.append(
            Print(
                self._screen,
                cpu_figure,
                half_height + 6,
                x=half_width - 23,
                stop_frame=20,
                speed=0,
                clear=False
            )
        )

        # Backdrop for CPU temperature
        self._screen.fill_polygon(
            [
                [
                    (half_width - 23, 21),
                    (half_width - 6, 21),
                    (half_width - 6, 25),
                    (half_width - 23, 25)
                ]
            ],
            colour=0
        )

        # CPU load
        self._screen.print_at(
            f"{cpu_load}",
            half_width - 23,
            half_height + 11
        )

        # GPU temperature
        self._effects.append(
            Print(
                self._screen,
                gpu_figure,
                half_height + 6,
                x=half_width + 14,
                stop_frame=20,
                speed=0,
                clear=False
            )
        )

        # Backdrop for GPU temperature
        self._screen.fill_polygon(
            [
                [
                    (half_width + 31, 21),
                    (half_width + 14, 21),
                    (half_width + 14, 25),
                    (half_width + 31, 25)
                ]
            ],
            colour=0
        )

        # GPU load
        self._screen.print_at(
            f"{gpu_load}",
            half_width + 14,
            half_height + 11
        )

    def reset(self, old_scene=None, screen=None):
        super(PymonitScene, self).reset(old_scene, screen)

        self._vitals = self._endpoint.get()
        self._effects = [self._effects[0]]

        self.render_system_info()
        self.render_vitals()
        self.render_sensor_value()


def run(screen):
    screen.play([PymonitScene(screen)], stop_on_resize=True)


if __name__ == "__main__":
    while True:
        try:
            Screen.wrapper(run)
            exit(0)
        except ResizeScreenError:
            pass
