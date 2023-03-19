from .shared import Shared
from .state_enums import State
from .platform import BrokenPlatform
import pygame
from .utils import render_at
from .player import Player
from .camera import Camera


class GameState:
    def __init__(self) -> None:
        self.next_state = None
        self.shared = Shared(camera=Camera())
        self.origin = pygame.Vector2(100, 150)
        self.plat = BrokenPlatform()
        self.player = Player(self.origin)
        self.shared.player = self.player

    def update(self):
        self.shared.camera.attach_to_player()
        self.player.update()

    def draw(self):
        self.plat.draw()
        self.player.draw()
