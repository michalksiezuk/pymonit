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
        self._endpoint = Endpoint()
        self._screen = screen
        self._vitals = self._endpoint.get()

        effects = [
            Print(
                screen,
                Rainbow(
                    screen,
                    FigletText("pymonit", font="poison"),
                ),
                screen.height // 2 - 14,
                speed=1
            ),
        ]

        super(PymonitScene, self).__init__(effects, 20, clear=False)

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

            self._screen.print_at(
                "> VITALS -------------------------------------------------------",
                self._screen.width // 2 - 33,
                self._screen.height // 2 + 4
            )

            self._screen.print_at(
                "CPU TEMP:",
                self._screen.width // 2 - 33,
                self._screen.height // 2 + 6
            )

            self._screen.print_at(
                "GPU TEMP:",
                self._screen.width // 2,
                self._screen.height // 2 + 6
            )

    def render_sensor_value(self):
        if len(self._vitals) != 0:
            cpu = self._vitals[0]
            cpu_temp = str(round(cpu["sensors"][0]["val"]))

            gpu = self._vitals[1]
            gpu_temp = str(round(gpu["sensors"][0]["val"]))
        else:
            cpu_temp = ""
            gpu_temp = ""

        cpu_figure = FigletText(f"{cpu_temp}", font="small")
        gpu_figure = FigletText(f"{gpu_temp}", font="small")

        # CPU temperature
        self._effects.append(
            Print(
                self._screen,
                cpu_figure,
                self._screen.height // 2 + 5,
                x=self._screen.width // 2 - 23,
                stop_frame=20,
                speed=0,
                clear=False
            )
        )

        # Backdrop for CPU temperature
        self._screen.fill_polygon(
            [
                [
                    (self._screen.width // 2 - 23, 20),
                    (self._screen.width // 2 - 12, 20),
                    (self._screen.width // 2 - 12, 24),
                    (self._screen.width // 2 - 23, 24)
                ]
            ],
            colour=0
        )

        # GPU temperature
        self._effects.append(
            Print(
                self._screen,
                gpu_figure,
                self._screen.height // 2 + 5,
                x=self._screen.width // 2 + 10,
                stop_frame=20,
                speed=0,
                clear=False
            )
        )

        # Backdrop for CPU temperature
        self._screen.fill_polygon(
            [
                [
                    (self._screen.width // 2 + 20, 20),
                    (self._screen.width // 2 + 9, 20),
                    (self._screen.width // 2 + 9, 24),
                    (self._screen.width // 2 + 20, 24)
                ]
            ],
            colour=0
        )

    def reset(self, old_scene=None, screen=None):
        super(PymonitScene, self).reset(old_scene, screen)

        self._vitals = self._endpoint.get()
        self._effects = [self._effects[0]]

        self.render_system_info()
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
