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
        self.rect = self.frames[0].get_rect(midbottom=self.pos)
        self.anim = Animation(self.frames, 0.3)

    def update(self):
        self.anim.update()

        if self.shared.cursor.player_target is not None:
            self.pos.move_towards_ip(
                self.shared.cursor.player_target, 30 * self.shared.dt
            )

        self.rect.midbottom = self.pos

    def draw(self):
        self.shared.game_screen.blit(self.anim.current_frame, self.shared.camera.transform(self.rect))
