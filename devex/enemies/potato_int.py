import math
import random

import pygame

from devex.enemies.base import Enemy
from devex.shared import Shared
from devex.utils import Projectile, Time, load_scale_3


class Tater(Projectile):
    IMAGES = tuple(load_scale_3(f"assets/potato-{n}.png") for n in range(1, 4))
    SPEED = 120
    DAMAGE = 2.5
    RANGE = 300

    def __init__(self, pos) -> None:
        self.shared = Shared()
        super().__init__(
            math.atan2(
                self.shared.player.pos.y - pos.y, self.shared.player.pos.x - pos.x
            ),
            self.SPEED,
        )
        self.original_image = random.choice(self.IMAGES).copy()
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rotat_angle = 0
        self.alive = True
        self.distance_travelled = 0

    def update(self):
        self.get_delta_velocity(self.shared.dt)
        self.distance_travelled += self.dv.magnitude()
        self.pos += self.dv
        self.rotat_angle += 30 * self.shared.dt
        self.image = pygame.transform.rotate(self.original_image, self.rotat_angle)
        self.rect = self.image.get_rect(center=self.pos)

        if self.rect.colliderect(self.shared.player.rect):
            self.shared.player.modify_health(-self.DAMAGE)
            self.shared.ss.add(0.5, 2.0)
            self.alive = False

        if self.distance_travelled > self.RANGE:
            self.alive = False

    def draw(self):
        self.shared.screen.blit(self.image, self.shared.camera.transform(self.rect))


class PotatoInt(Enemy):
    IMAGE = load_scale_3("assets/integer.png")
    SPEED = 30
    SENSE_RANGE = 500

    def __init__(
        self, broken_platform_size: int, tile_rect: pygame.Rect, origin: tuple[int, int]
    ) -> None:
        iso_pos = (
            random.randrange(2, broken_platform_size - 2) + origin[0],
            random.randrange(2, broken_platform_size - 2) + origin[1],
        )
        super().__init__(
            int,
            "pink",
            PotatoInt.IMAGE,
            iso_pos,
            broken_platform_size,
            tile_rect,
            PotatoInt.SPEED,
            origin,
        )

        self.value = random.choice(
            (random.randrange(100, 10000), random.randrange(1, 10))
        )
        self.set_font_surf()
        self.potatos: list[Tater] = []
        self.potato_cooldown = Time(2.0)

    def start_condition(self):
        return self.health < self.max_health

    def continue_condition(self):
        if not self.potato_cooldown.tick():
            return
        return self.pos.distance_to(self.shared.player.pos) < self.SENSE_RANGE

    def gen_taters(self):
        for _ in range(random.randrange(1, 4)):
            pos = self.pos + (random.randrange(30), random.randrange(30))
            self.potatos.append(Tater(pos))

    def update(self):
        super().update()
        if self.start_condition() and self.continue_condition():
            self.gen_taters()

        for potato in self.potatos[:]:
            potato.update()
            if not potato.alive:
                self.potatos.remove(potato)

    def draw(self):
        super().draw()
        for potato in self.potatos:
            potato.draw()
