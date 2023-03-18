import pygame
from .utils import Animation
from .shared import Shared


class Player:
    def __init__(self, origin: pygame.Vector2) -> None:
        self.shared = Shared()
        self.pos = origin.copy()
        self.frames = [
            pygame.image.load(f"assets/player-anim-{n}.png").convert_alpha()
            for n in range(1, 7)
        ]
        self.anim = Animation(self.frames, 0.3)

    def update(self):
        self.anim.update()

    def draw(self):
        self.shared.game_screen.blit(self.anim.current_frame, self.pos)
