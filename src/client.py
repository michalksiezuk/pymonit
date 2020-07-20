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
        self._screen_half_width = self._screen.width // 2
        self._screen_half_height = self._screen.height // 2

        self._endpoint = Endpoint()
        self._vitals = self._endpoint.get()

        self._effects = [
            Print(
                screen,
                Rainbow(
                    screen,
                    FigletText("pymonit", font="isometric3"),
                ),
                screen.height // 2 - 13,
                speed=1
            )
        ]

        super(PymonitScene, self).__init__(self._effects, 10, clear=False)

    def render_system_info(self):
        cpu_name = gpu_name = ""

        if len(self._vitals) != 0:
            cpu_name = self._vitals[0]["name"]
            gpu_name = self._vitals[1]["name"]

        self._screen.print_at(
            f"{cpu_name}",
            self._screen_half_width - 35,
            self._screen_half_height + 1
        )

        self._screen.print_at(
            f"{gpu_name}",
            self._screen_half_width + 6,
            self._screen_half_height + 1
        )

    def render_vitals(self):
        self._screen.print_at(
            "CPU TEMP:",
            self._screen_half_width - 35,
            self._screen_half_height + 9
        )

        self._screen.print_at(
            "CPU LOAD:",
            self._screen_half_width - 35,
            self._screen_half_height + 11
        )

        self._screen.print_at(
            "GPU TEMP:",
            self._screen_half_width + 6,
            self._screen_half_height + 9
        )

        self._screen.print_at(
            "GPU LOAD:",
            self._screen_half_width + 6,
            self._screen_half_height + 11
        )

    def render_sensor_value(self):
        cpu_temp = cpu_load = gpu_temp = gpu_load = ""

        if len(self._vitals) != 0:
            cpu = self._vitals[0]
            cpu_temp = str(round(cpu["sensors"][0]["val"]))
            cpu_load = self._format_load_string(self, cpu["sensors"][1])

            gpu = self._vitals[1]
            gpu_temp = str(round(gpu["sensors"][0]["val"]))
            gpu_load = self._format_load_string(self, gpu["sensors"][1])

        # CPU load
        self._screen.print_at(
            f"{cpu_load}",
            self._screen_half_width - 23,
            self._screen_half_height + 11
        )

        # GPU load
        self._screen.print_at(
            f"{gpu_load}",
            self._screen_half_width + 18,
            self._screen_half_height + 11
        )

        # Backdrops for CPU and GPU temperature
        self._screen.fill_polygon(
            [
                [
                    (self._screen_half_width - 26, 18),
                    (self._screen_half_width - 1, 18),
                    (self._screen_half_width - 1, 25),
                    (self._screen_half_width - 26, 25)
                ],
                [
                    (self._screen_half_width + 38, 18),
                    (self._screen_half_width + 15, 18),
                    (self._screen_half_width + 15, 25),
                    (self._screen_half_width + 38, 25)
                ]
            ],
            colour=0
        )

        cpu_figure = FigletText(f"{cpu_temp}", font="larry3d")
        gpu_figure = FigletText(f"{gpu_temp}", font="larry3d")

        # CPU temperature
        self._effects.append(
            Print(
                self._screen,
                cpu_figure,
                self._screen_half_height + 3,
                x=self._screen_half_width - 26,
                speed=0,
                clear=False
            )
        )

        # GPU temperature
        self._effects.append(
            Print(
                self._screen,
                gpu_figure,
                self._screen_half_height + 3,
                x=self._screen_half_width + 15,
                speed=0,
                clear=False
            )
        )

    def reset(self, old_scene=None, screen=None):
        super(PymonitScene, self).reset(old_scene, screen)

        self._vitals = self._endpoint.get()
        self._effects = [self._effects[0]]

        self.render_system_info()
        self.render_vitals()
        self.render_sensor_value()

    @staticmethod
    def _format_load_string(self, sensor):
        load_current = round(sensor["val"], 2)
        load_min = round(sensor["min"], 2)
        load_max = round(sensor["max"], 2)

        return f"{load_current}/{load_min}/{load_max}   "


def run(screen):
    screen.play([PymonitScene(screen)], stop_on_resize=True)


if __name__ == "__main__":
    while True:
        try:
            Screen.wrapper(run)
            exit(0)
        except ResizeScreenError:
            pass
