import pygame
from .utils import Animation, load_scale_3
from .bloom import Bloom
from .shared import Shared


class Player:
    def __init__(self, origin: pygame.Vector2) -> None:
        self.shared = Shared()
        self.pos = origin.copy()
        self.frames = [load_scale_3(f"assets/player-anim-{n}.png") for n in range(1, 7)]
        self.rect = self.frames[0].get_rect(midbottom=self.pos)
        self.anim = Animation(self.frames, 0.3)
        self.bloom = Bloom(2)

    def update(self):
        self.anim.update()

        if self.shared.cursor.player_target is not None:
            self.pos.move_towards_ip(
                self.shared.cursor.player_target, 150 * self.shared.dt
            )

        self.rect.midbottom = self.pos
        self.bloom.update(self.shared.camera.transform(self.rect.center))

    def draw(self):
        self.shared.screen.blit(
            self.anim.current_frame, self.shared.camera.transform(self.rect)
        )
        self.bloom.draw(self.shared.overlay)
