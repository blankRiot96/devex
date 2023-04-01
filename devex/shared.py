import ctypes
import platform
import subprocess
import sys
from typing import Self

import pygame


def get_screen_size_linux():
    cmd = ["xrandr"]
    cmd2 = ["grep", "*"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd2, stdin=p.stdout, stdout=subprocess.PIPE)
    p.stdout.close()
    resolution_string, junk = p2.communicate()
    resolution = resolution_string.split()[0]
    width, height = resolution.split("x")

    return width, height


def get_screen_size_win():
    user32 = ctypes.windll.user32
    width, height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    return width, height


def get_screen_size_wasm():
    return platform.window.innerWidth, platform.window.innerHeight


class Shared:
    _inst = None

    Constants
    if sys.platform == "win32":
        SCREEN_WIDTH, SCREEN_HEIGHT = get_screen_size_win()
    elif "linux" in sys.platform:
        SCREEN_WIDTH, SCREEN_HEIGHT = get_screen_size_linux()
    elif sys.platform in ("emscripten", "wasi"):
        SCREEN_WIDTH, SCREEN_HEIGHT = get_screen_size_wasm()
    else:
        raise EnvironmentError("Game only supported in Windows and Linux.")

    SCRECT = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

    screen: pygame.Surface
    overlay: pygame.Surface

    events: list[pygame.event.Event]
    dt: float

    def __new__(cls: type[Self], *args, **kwargs) -> Self:
        if Shared._inst is None:
            Shared._inst = super().__new__(cls)

        return Shared._inst

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)
