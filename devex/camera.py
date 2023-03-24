import pygame

from .shared import Shared


class Camera:
    DRAG = 0.03

    def __init__(self) -> None:
        self.offset = pygame.Vector2()
        self.shared = Shared()

    def transform(self, coord):
        return coord[0] - self.offset.x, coord[1] - self.offset.y

    def transform_mini(self, coord):
        return coord[0] - self.offset.x, coord[1] - self.offset.y

    def attach_to_mini(self, MAP_SIZE):
        self.offset.x += (
            (self.shared.current_chunks[0].origin[0] * 8)
            - self.offset.x
            - (MAP_SIZE[0] // 2)
        ) * self.DRAG
        self.offset.y += (
            (self.shared.current_chunks[0].origin[1] * 8)
            - self.offset.y
            - (MAP_SIZE[1] // 2)
        ) * self.DRAG

    def attach_to_player(self):
        self.offset.x += (
            self.shared.player.pos.x - self.offset.x - (self.shared.SCREEN_WIDTH // 2)
        ) * self.DRAG
        self.offset.y += (
            self.shared.player.pos.y - self.offset.y - (self.shared.SCREEN_HEIGHT // 2)
        ) * self.DRAG
