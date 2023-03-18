from .shared import Shared
from .state_enums import State
from .platform import BrokenPlatform
import pygame
from .utils import render_at
from .player import Player


class GameState:
    def __init__(self) -> None:
        self.next_state = None
        self.shared = Shared(game_screen=pygame.Surface((600, 500), pygame.SRCALPHA))
        self.origin = pygame.Vector2(100, 150)
        self.plat = BrokenPlatform()
        self.player = Player(self.origin)

    def update(self):
        self.player.update()

    def draw(self):
        self.shared.game_screen.fill("black")
        self.plat.draw()
        self.player.draw()

        render_at(
            self.shared.screen,
            pygame.transform.scale(self.shared.game_screen, (1800, 1500)),
            "center",
        )
