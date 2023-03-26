import random
import string

import pygame

from devex.enemies.base import Enemy
from devex.utils import load_scale_3


class CentiSet(Enemy):
    IMAGE = load_scale_3("assets/set.png")
    SPEED = 25

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
            CentiSet.IMAGE,
            iso_pos,
            broken_platform_size,
            tile_rect,
            CentiSet.SPEED,
            origin,
            bouncy_direction="horizontal",
        )

        self.value = {random.randrange(1, 10) for _ in range(random.randrange(2, 5))}
        self.set_font_surf()
