from .shared import Shared
from .platform import PlatformManager
import pygame
from .player import Player
from .camera import Camera


class GameState:
    def __init__(self) -> None:
        self.next_state = None
        self.shared = Shared(camera=Camera())
        self.origin = pygame.Vector2(100, 150)
        self.plat = PlatformManager()
        self.player = Player(self.origin)
        self.shared.player = self.player
        self.shared.overlay = self.shared.screen.copy()
        self.shared.overlay.fill("black")
        self.shared.overlay.set_alpha(150)
        self.shared.provisional_chunk = self.shared.screen.copy()

    def update(self):
        self.shared.camera.attach_to_player()
        self.plat.update()
        self.player.update()

    def draw(self):
        self.shared.overlay.fill("black")
        self.plat.draw()
        if self.plat.done:
            self.player.draw()
            self.plat.draw_torches()
            self.shared.screen.blit(
                self.shared.overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MIN
            )
