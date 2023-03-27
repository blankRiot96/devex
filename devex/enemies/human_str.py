import math
import random
import string

import pygame

from devex.enemies.base import Enemy
from devex.shared import Shared
from devex.utils import Projectile, Time, get_font, load_scale_3


class Alphabet(Projectile):
    SPEED = 140
    DAMAGE = 4.5
    RANGE = 250
    FONT = get_font("assets/Hack/Hack Bold Nerd Font Complete Mono.ttf", 40)

    def __init__(self, pos) -> None:
        self.shared = Shared()
        super().__init__(
            math.atan2(
                self.shared.player.pos.y - pos.y, self.shared.player.pos.x - pos.x
            ),
            self.SPEED,
        )
        self.gen_img()
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rotat_angle = 0
        self.alive = True
        self.distance_travelled = 0

    def gen_img(self):
        alpha = random.choice(string.ascii_letters)
        color = random.choice(tuple(pygame.colordict.THECOLORS.keys()))

        self.original_image = self.FONT.render(alpha, True, color)

    def update(self):
        self.get_delta_velocity(self.shared.dt)
        self.distance_travelled += self.dv.magnitude()
        self.pos += self.dv
        self.rotat_angle += 50 * self.shared.dt
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


class HumanStr(Enemy):
    IMAGE = load_scale_3("assets/str.png")
    SPEED = 35
    SENSE_RANGE = 400

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
            HumanStr.IMAGE,
            iso_pos,
            broken_platform_size,
            tile_rect,
            HumanStr.SPEED,
            origin,
        )

        list_str = list(string.ascii_lowercase[: random.randrange(4, 8)])
        random.shuffle(list_str)
        list_str = "".join(list_str)
        self.value = f'"{list_str}"'
        self.set_font_surf()

        self.alphabets: list[Alphabet] = []
        self.alpha_cooldown = Time(1.5)

    def start_condition(self):
        if not self.alpha_cooldown.tick():
            return
        return self.pos.distance_to(self.shared.player.pos) < self.SENSE_RANGE

    def gen_alphabets(self):
        for _ in range(random.randrange(1, 4)):
            pos = self.pos + (random.randrange(60), random.randrange(60))
            self.alphabets.append(Alphabet(pos))

    def update(self):
        super().update()
        if self.start_condition():
            self.gen_alphabets()

        for alpha in self.alphabets[:]:
            alpha.update()
            if not alpha.alive:
                self.alphabets.remove(alpha)

    def draw(self):
        super().draw()
        for alpha in self.alphabets:
            alpha.draw()
