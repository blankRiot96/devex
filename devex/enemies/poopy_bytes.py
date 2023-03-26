import random
import string

import pygame

from devex.enemies.base import Enemy
from devex.utils import load_scale_3


class PoopyBytes(Enemy):
    IMAGE = load_scale_3("assets/bytes.png")
    SPEED = 45

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
            PoopyBytes.IMAGE,
            iso_pos,
            broken_platform_size,
            tile_rect,
            PoopyBytes.SPEED,
            origin,
        )

        list_str = list(string.ascii_lowercase[: random.randrange(4, 8)])
        random.shuffle(list_str)
        list_str = "".join(list_str)
        self.value = f'b"{list_str}"'
        self.set_font_surf()
