import random
import string

import pygame

from devex.enemies.base import Enemy
from devex.utils import load_scale_3


class PoopyBytes(Enemy):
    IMAGE = load_scale_3("assets/bytes.png")
    SPEED = 45
    ATTACK_SPEED = 80
    DAMAGE = 10

    def __init__(
        self, broken_platform_size: int, tile_rect: pygame.Rect, origin: tuple[int, int]
    ) -> None:
        iso_pos = (
            random.randrange(2, broken_platform_size - 2) + origin[0],
            random.randrange(2, broken_platform_size - 2) + origin[1],
        )
        super().__init__(
            int,
            "purple",
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

    def start_condition(self):
        return self.health < self.max_health

    def attack_player(self):
        self.pos.move_towards_ip(
            self.shared.player.pos, self.ATTACK_SPEED * self.shared.dt
        )
        self.rect.midbottom = self.pos
        self.font_rect.midtop = self.pos

        if self.rect.colliderect(self.shared.player.rect):
            self.shared.player.modify_health(-self.DAMAGE)
            self.shared.ss.add(0.3, 0.5)
            self.alive = False

    def update(self):
        if self.start_condition():
            self.attack_player()
        else:
            self.move()

        self.morph_image()
        self.take_damage()
        self.highlight_red()
