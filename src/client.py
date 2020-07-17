import asyncio
from sys import exit

import aiohttp
from asciimatics.effects import Print
from asciimatics.renderers import FigletText, Rainbow
from asciimatics.scene import Scene
from asciimatics.screen import Screen

PYMONIT_ENDPOINT = "http://192.168.0.100:8080"

vitals = []


async def get_vitals():
    while True:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(PYMONIT_ENDPOINT) as response:
                    global vitals
                    vitals = await response.json()
            except aiohttp.ClientConnectorError as error:
                print('Connection Error', str(error))

            await asyncio.sleep(1)


def getEffects(screen):
    global vitals

    if len(vitals) != 0:
        cpu = vitals[0]
        gpu = vitals[1]

        cpu_name = cpu["name"]
        cpu_temp = str(round(cpu["sensors"][0]["val"]))

        gpu_name = gpu["name"]
        gpu_temp = str(round(gpu["sensors"][0]["val"]))
    else:
        cpu_name = ""
        cpu_temp = "00"

        gpu_name = ""
        gpu_temp = "00"

    return [
        Print(
            screen,
            Rainbow(
                screen,
                FigletText("pymonit", font="poison"),
            ),
            screen.height // 2 - 15,
            speed=0
        ),
        Print(
            screen,
            FigletText(f"{cpu_name}", font="mini"),
            screen.height // 2 - 2,
            speed=0
        ),
        Print(
            screen,
            FigletText(f"{gpu_name}", font="mini"),
            screen.height // 2 + 1,
            speed=0
        ),
        Print(
            screen,
            FigletText(f"CPU", font='small'),
            screen.height // 2 + 8,
            screen.width // 2 - 37,
            speed=1
        ),
        Print(
            screen,
            FigletText(f"{cpu_temp}", font='big'),
            screen.height // 2 + 6,
            screen.width // 2 - 19,
            speed=1
        ),
        Print(
            screen,
            FigletText(f"GPU", font='small'),
            screen.height // 2 + 8,
            screen.width // 2 + 4,
            speed=1
        ),
        Print(
            screen,
            FigletText(f"{gpu_temp}", font='big'),
            screen.height // 2 + 6,
            screen.width // 2 + 22,
            speed=1
        ),
    ]


def update_view(loop, screen):
    screen.set_scenes([Scene(getEffects(screen), 500)])
    screen.draw_next_frame()

    loop.call_later(1, update_view, loop, screen)


def run():
    screen = Screen.open()
    screen.set_scenes([
        Scene(getEffects(screen), 500)
    ])

    loop = asyncio.get_event_loop()
    loop.create_task(get_vitals())
    loop.call_soon(update_view, loop, screen)

    loop.run_forever()
    loop.close()
    screen.close()


if __name__ == "__main__":
    run()
    exit(0)
