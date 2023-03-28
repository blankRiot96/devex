import itertools
import random
import string
from abc import ABC

import pygame
from logit import log

from devex.shared import Shared
from devex.utils import PlayItOnceAnimation, SinWave, get_font, iso_to_screen


class Enemy(ABC):
    font = get_font("assets/Hack/Hack Bold Nerd Font Complete.ttf", 16)

    def __init__(
        self,
        data_type: type,
        data_font_color,
        image: pygame.Surface,
        iso_pos: tuple[int, int],
        broken_platform_size: int,
        tile_rect: pygame.Rect,
        enemy_speed: float,
        origin: tuple[int, int],
        health: int = 100,
        bouncy_direction: str = "vertical",
    ) -> None:
        self.shared = Shared()
        self.data_type = data_type
        self.data_font_color = data_font_color
        self.original_image = image.copy()
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.broken_platform_size = broken_platform_size
        self.origin = origin
        self.bouncy_direction = bouncy_direction
        self.health = health
        self.max_health = health
        self.alive = True

        """
        So, the iso_pos is basically gonna hold a value such as
        (2, 3). Here the enemy will move across a few tiles. Maybe the path is:
        (2, 3) -> (3, 3) -> (4, 3) -> (5, 3)
        """
        self.iso_pos = iso_pos
        self.iso_path_range = self.calc_path_range()
        self.initial_screen_pos = iso_to_screen(self.iso_path_range[0], tile_rect)
        self.final_screen_pos = iso_to_screen(self.iso_path_range[-1], tile_rect)
        self.targets = itertools.cycle((self.initial_screen_pos, self.final_screen_pos))
        self.current_target = self.initial_screen_pos
        self.pos = pygame.Vector2(self.initial_screen_pos)
        self.speed = enemy_speed

        """Image morphing"""
        if bouncy_direction == "vertical":
            self.size = self.image.get_height()
        else:
            self.size = self.image.get_width()
        self.original_size = self.size
        self.bouncy_wave = SinWave(0.06)
        self.taking_damage = False
        self.higlight_alpha = 200
        self.highlight_reduction_speed = 100

    def calc_path_range(self) -> None:
        """Calculates the path range for the enemy."""

        # Random parameters
        n_steps: int = random.randrange(3, self.broken_platform_size - 2)
        x_or_y: int = random.randint(0, 1)

        # Applies the parameters
        axis_range_x = range(1 + self.origin[0], n_steps + self.origin[0])
        axis_range_y = range(1 + self.origin[1], n_steps + self.origin[1])

        # Produces the result
        if x_or_y:
            return [(self.iso_pos[0], axis) for axis in axis_range_y]

        return [(axis, self.iso_pos[1]) for axis in axis_range_x]

    def highlight_red(self):
        if not self.taking_damage:
            return

        surf = pygame.Surface(self.image.get_size())
        surf.fill("red")
        surf.set_alpha(self.higlight_alpha)
        self.higlight_alpha -= self.highlight_reduction_speed * self.shared.dt
        if self.higlight_alpha <= 120:
            self.taking_damage = False
            self.higlight_alpha = 200
        self.image.blit(surf, (0, 0))

    def on_damage(self, fireball):
        fireball.alive = False
        self.shared.play_it_once_anims.append(
            PlayItOnceAnimation(fireball.EXPLOSION_FRAMES, 0.08, self.pos - (64, 64))
        )
        self.health -= fireball.damage
        self.taking_damage = True
        self.shared.ss.add(1.0, 1.5)

    def take_damage(self):
        for fireball in self.shared.player.fireball_manager.fireballs:
            if fireball.rect.colliderect(self.rect):
                self.on_damage(fireball)

        if self.health <= 0:
            self.alive = False
            try:
                self.shared.values[type(self)].append(self.value)
            except KeyError as e:
                log.debug(e)

            if self.shared.inv_widget is not None:
                self.shared.inv_widget.construct()

    def set_font_surf(self):
        self.font_surf = self.font.render(str(self.value), True, self.data_font_color)
        self.font_rect = self.font_surf.get_rect()

    def move(self):
        self.pos.move_towards_ip(self.current_target, self.speed * self.shared.dt)
        if self.pos == self.current_target:
            self.current_target = next(self.targets)

        self.rect.midbottom = self.pos
        self.font_rect.midtop = self.pos

    def morph_image(self):
        """Create a bouncy animation for the enemy"""

        self.size = self.original_size + (self.bouncy_wave.val() * 5)
        if self.bouncy_direction == "vertical":
            new_size = self.original_image.get_width(), self.size
        elif self.bouncy_direction == "horizontal":
            new_size = self.size, self.original_image.get_height()
        else:
            return
        self.image = pygame.transform.scale(self.original_image, new_size)

    def update(self):
        self.move()
        self.morph_image()
        self.take_damage()
        self.highlight_red()

    def draw(self):
        self.shared.screen.blit(self.image, self.shared.camera.transform(self.rect))
        self.shared.screen.blit(
            self.font_surf, self.shared.camera.transform(self.font_rect)
        )
