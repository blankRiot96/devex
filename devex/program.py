import inspect
import random

import pygame

from . import game_funcs
from .shared import Shared
from .utils import scale_by


class Code:
    FUNCS = tuple(m for m in dir(game_funcs) if not m.startswith("__"))
    IMAGE = pygame.image.load("assets/code.png").convert_alpha()
    IMAGE = scale_by(IMAGE, 0.5)

    def __init__(self, pos) -> None:
        self.func = getattr(game_funcs, random.choice(Code.FUNCS))
        self.code_text = inspect.getsource(self.func)
        self.parameter_data = self.func.__annotations__
        self.pos = pygame.Vector2(pos)
        self.shared = Shared()

    def update(self):
        ...

    def draw(self):
        self.shared.screen.blit(self.IMAGE, self.pos)


if __name__ == "__main__":
    c = Code()
