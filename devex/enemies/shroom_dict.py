import math
import random

import pygame

from devex.enemies.base import Enemy
from devex.shared import Shared
from devex.utils import Projectile, Time, load_scale_3


class Spore(Projectile):
    INITIAL_SPEED = 100
    IMAGE = load_scale_3("assets/spore.png")
    DEATH_SPEED = 100
    DAMAGE = 10

    def __init__(self, radians, pos) -> None:
        super().__init__(radians, self.INITIAL_SPEED)
        self.image = self.IMAGE.copy()
        self.shared = Shared()
        self.pos = pos.copy()
        self.rect = self.image.get_rect()
        self.alive = True
        self.alpha = 255

    def update(self):
        self.get_delta_velocity(self.shared.dt)
        self.pos += self.dv
        self.rect.center = self.pos
        self.alpha -= self.DEATH_SPEED * self.shared.dt
        self.image.set_alpha(self.alpha)

        if self.alpha < 10:
            self.alive = False

        if self.rect.colliderect(self.shared.player.rect):
            self.shared.player.modify_health(-self.DAMAGE)
            self.shared.ss.add(0.3, 1.1)
            self.alive = False

    def draw(self):
        self.shared.screen.blit(self.image, self.shared.camera.transform(self.rect))


class SporeManager:
    SPORES_PER_BATCH = 8

    def __init__(self) -> None:
        self.spores: list[Spore] = []
        self.cooldown = Time(1.5)

    def create_spore_batch(self, pos):
        base_rad = (2 * math.pi) / self.SPORES_PER_BATCH
        for i in range(self.SPORES_PER_BATCH):
            self.spores.append(Spore(i * base_rad, pos))

    def update(self, pos, start):
        for spore in self.spores[:]:
            spore.update()
            if not spore.alive:
                self.spores.remove(spore)

        if self.cooldown.tick() and start:
            self.create_spore_batch(pos)

    def draw(self):
        for spore in self.spores:
            spore.draw()


class ShroomDict(Enemy):
    IMAGE = load_scale_3("assets/dict.png")
    SPEED = 120
    SENSE_RANGE = 600

    def __init__(
        self, broken_platform_size: int, tile_rect: pygame.Rect, origin: tuple[int, int]
    ) -> None:
        iso_pos = (
            random.randrange(2, broken_platform_size - 2) + origin[0],
            random.randrange(2, broken_platform_size - 2) + origin[1],
        )
        super().__init__(
            dict,
            "midnightblue",
            ShroomDict.IMAGE,
            iso_pos,
            broken_platform_size,
            tile_rect,
            ShroomDict.SPEED,
            origin,
        )
        self.value = {
            random.randrange(10): random.randrange(10)
            for _ in range(random.randrange(1, 4))
        }
        self.set_font_surf()
        self.spore_manager = SporeManager()

    def start_condition(self):
        return self.pos.distance_to(self.shared.player.pos) < self.SENSE_RANGE

    def update(self):
        super().update()
        self.spore_manager.update(self.pos, self.start_condition())

    def draw(self):
        super().draw()
        self.spore_manager.draw()
