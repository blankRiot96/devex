import random

import pygame

from devex.enemies.base import Enemy
from devex.shared import Shared
from devex.utils import load_scale_3, render_at, scale_by


class HealthBar:
    BAR_SIZE = 250, 10

    def __init__(self, max_health) -> None:
        self.max_health = max_health
        self.shared = Shared()
        self.background_surf = pygame.Surface(self.BAR_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(
            self.background_surf,
            (255, 200, 200),
            pygame.Rect(0, 0, *self.BAR_SIZE),
            border_radius=7,
        )
        self.original_foreground_surf = pygame.Surface(self.BAR_SIZE)
        self.original_foreground_surf.fill((80, 20, 20))
        self.foreground_surf = self.original_foreground_surf.copy()
        self.size = self.BAR_SIZE

    def update(self, health):
        self.size = (health / self.max_health) * self.BAR_SIZE[0], self.BAR_SIZE[1]

        self.foreground_surf = pygame.Surface(self.BAR_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(
            self.foreground_surf,
            (80, 20, 20),
            pygame.Rect(0, 0, *self.size),
            border_radius=7,
        )
        self.foreground_rect = self.foreground_surf.get_rect(
            midbottom=self.shared.final_boss.rect.midtop
        )

    def draw(self):
        self.shared.screen.blit(
            self.background_surf, self.shared.camera.transform(self.foreground_rect)
        )
        self.shared.screen.blit(
            self.foreground_surf, self.shared.camera.transform(self.foreground_rect)
        )


class FinalBoss(Enemy):
    IMAGE = load_scale_3("assets/tuple.png")

    def __init__(self, side, tile_rect, origin) -> None:
        iso_pos = (
            side // 2,
            side // 2,
        )
        super().__init__(
            tuple,
            "black",
            self.IMAGE.copy(),
            iso_pos=iso_pos,
            broken_platform_size=side,
            tile_rect=tile_rect,
            enemy_speed=100,
            origin=origin,
            health=5_000,
            bouncy_direction=None,
        )

        self.value = tuple(random.randrange(1, 256) for _ in range(4))
        self.set_font_surf()
        self.health_bar = HealthBar(self.health)

    def move(self):
        self.pos.move_towards_ip(self.shared.player.pos, self.speed * self.shared.dt)
        self.rect.midbottom = self.pos
        self.font_rect.midtop = self.pos

    def update(self):
        self.image = self.original_image.copy()
        super().update()
        self.health_bar.update(self.health)

    def draw(self):
        super().draw()
        self.health_bar.draw()
