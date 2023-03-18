from .shared import Shared
from .state_enums import State
from .platform import BrokenPlatform
import pygame
from .utils import render_at


class GameState:
    def __init__(self) -> None:
        self.next_state = None
        self.shared = Shared(game_screen=pygame.Surface((600, 500), pygame.SRCALPHA))
        self.plat = BrokenPlatform()

    def update(self):
        ...

    def draw(self):
        self.plat.draw()
        render_at(
            self.shared.screen,
            pygame.transform.scale(self.shared.game_screen, (1800, 1500)),
            "center"
        )
