import random

import pygame

from . import game_funcs
from .bloom import Bloom
from .shared import Shared
from .utils import get_font, scale_by


class Code:
    FUNCS = list(m for m in dir(game_funcs) if not m.startswith("__"))
    FUNCS.remove("sources")
    IMAGE = pygame.image.load("assets/code.png").convert_alpha()
    IMAGE = scale_by(IMAGE, 0.025)
    FONT = get_font("assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 16)

    def __init__(self, pos) -> None:
        self.func = getattr(game_funcs, random.choice(Code.FUNCS))
        self.get_source()
        self.parameter_data = self.func.__annotations__
        self.pos = pygame.Vector2(pos)
        self.shared = Shared()
        self.rect = self.IMAGE.get_rect(midbottom=self.pos)
        self.bloom = Bloom(0.4, wave_speed=0.01, expansion_factor=10)
        self.pickup_surf = Code.FONT.render("[F] PICKUP", True, "purple", "white")
        self.pickup_rect = self.pickup_surf.get_rect(midbottom=self.rect.midtop)
        self.near = False
        self.alive = True

    def get_source(self):
        self.code_text = game_funcs.sources[self.func]

    def check_near(self):
        self.near = self.shared.player.rect.colliderect(self.rect)

    def on_pickup(self):
        for event in self.shared.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f and self.near:
                    if len(self.shared.collected_programs) < 6:
                        self.shared.collected_programs.append(self)
                    # else: LOG MESSAGE
                    if self.shared.inv_widget is not None:
                        self.shared.inv_widget.construct()
                    self.alive = False

    def update(self):
        self.bloom.update(self.shared.camera.transform(self.rect.center))
        self.check_near()
        self.on_pickup()

    def draw(self):
        self.shared.screen.blit(self.IMAGE, self.shared.camera.transform(self.rect))
        self.bloom.draw(self.shared.overlay)

        if self.near:
            self.shared.screen.blit(
                self.pickup_surf, self.shared.camera.transform(self.pickup_rect)
            )


if __name__ == "__main__":
    c = Code()
