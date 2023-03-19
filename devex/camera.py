import pygame
from .shared import Shared


class Camera:
    DRAG = 0.03

    def __init__(self) -> None:
        self.offset = pygame.Vector2()
        self.shared = Shared()

    def transform(self, coord):
        return coord[0] - self.offset.x, coord[1] - self.offset.y

    def attach_to_player(self):
        self.offset.x += (
            self.shared.player.pos.x - self.offset.x - (self.shared.SCREEN_WIDTH // 2)
        ) * self.DRAG
        self.offset.y += (
            self.shared.player.pos.y - self.offset.y - (self.shared.SCREEN_HEIGHT // 2)
        ) * self.DRAG
