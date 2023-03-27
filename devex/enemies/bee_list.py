import random
import string

import pygame

from devex.enemies.base import Enemy
from devex.enemies.falling_sword import Sword
from devex.utils import load_scale_3


class BeeList(Enemy):
    IMAGE = load_scale_3("assets/list.png")
    SPEED = 15
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
            BeeList.IMAGE,
            iso_pos,
            broken_platform_size,
            tile_rect,
            BeeList.SPEED,
            origin,
        )

        self.value = [random.randrange(1, 10) for _ in range(random.randrange(2, 5))]
        self.set_font_surf()
        self.sword = None

    def start_condition(self):
        if self.sword is not None:
            return False
        return self.pos.distance_to(self.shared.player.pos) < self.SENSE_RANGE

    def update(self):
        super().update()

        if self.start_condition():
            self.sword = Sword(
                1,
                15,
                self.shared.player.pos
                + (random.uniform(-30, 30), random.uniform(-30, 30)),
            )

        if self.sword is None:
            return

        self.sword.update()
        if not self.sword.alive:
            self.sword = None

    def draw(self):
        super().draw()
        if self.sword is None:
            return
        self.sword.draw()
