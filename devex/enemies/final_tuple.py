import math
import random

import pygame

from devex.enemies.base import Enemy
from devex.enemies.falling_sword import Sword
from devex.player_attacks import Fireball
from devex.shared import Shared
from devex.utils import Time, load_scale_3


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
    SENSE_RANGE = 1_500

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
            health=1_500,
            bouncy_direction=None,
        )

        self.value = tuple(random.randrange(1, 256) for _ in range(4))
        self.set_font_surf()
        self.health_bar = HealthBar(self.health)
        self.heal_timer = Time(10.0)
        self.attack_timer = Time(20.0)
        self.healing = False
        self.current_attacks = [self.throw_fireballs, self.heavenly_swords]

        self.fb_timer = Time(4.0)
        self.spread_timer = Time(2.0)
        self.fireballs: list[Fireball] = []

        self.sword = None

    def _create_fireball(self):
        offset_x = random.uniform(-30, 30)
        offset_y = random.uniform(-30, 30)
        radians = math.atan2(
            self.shared.player.pos.y - self.pos.y, self.shared.player.pos.x - self.pos.x
        )
        self.fireballs.append(
            Fireball(radians, self.pos + (offset_x, offset_y), damage=3, speed=500)
        )

    def throw_fireballs(self):
        if self.fb_timer.tick():
            n_fireballs = random.randrange(2, 5)
            for _ in range(n_fireballs):
                self._create_fireball()

    def _create_spread_ball(self, n):
        radians = 2 * math.pi * n / 6
        self.fireballs.append(Fireball(radians, self.pos, damage=3))

    def spread_fireballs(self):
        if self.spread_timer.tick():
            n_fireballs = 6
            for n in range(n_fireballs):
                self._create_spread_ball(n)

    def update_fb(self):
        for fb in self.fireballs[:]:
            fb.update()

            if not fb.alive:
                self.fireballs.remove(fb)
                continue
            if fb.rect.colliderect(self.shared.player.rect):
                self.shared.player.modify_health(-fb.damage)
                self.fireballs.remove(fb)

    def start_condition(self):
        if self.sword is not None:
            return False
        return self.pos.distance_to(self.shared.player.pos) < self.SENSE_RANGE

    def heavenly_swords(self):
        if self.start_condition():
            self.sword = Sword(
                random.randint(0, 1),
                10,
                self.shared.player.pos
                + (random.uniform(-30, 30), random.uniform(-30, 30)),
            )

        if self.sword is None:
            return

        self.sword.update()
        if not self.sword.alive:
            self.sword = None

    def heal(self):
        if self.heal_timer.tick():
            self.healing = False
            self.current_attacks = random.choices(
                (self.throw_fireballs, self.spread_fireballs, self.heavenly_swords), k=2
            )
            self.attack_timer.reset()
            self.fb_timer.reset()
            self.spread_timer.reset()

        self.health += 150 * self.shared.dt
        if self.health > self.max_health:
            self.health = self.max_health

    def update_behaviour(self):
        if not self.healing:
            self.update_fb()
        if self.healing:
            self.heal()
        elif self.attack_timer.tick():
            self.healing = True
            self.heal_timer.reset()
        else:
            for attack in self.current_attacks:
                attack()

    def move(self):
        if self.healing:
            return
        self.pos.move_towards_ip(self.shared.player.pos, self.speed * self.shared.dt)
        self.rect.midbottom = self.pos
        self.font_rect.midtop = self.pos

    def update(self):
        self.image = self.original_image.copy()
        super().update()
        self.health_bar.update(self.health)
        self.update_behaviour()

    def draw(self):
        super().draw()
        self.health_bar.draw()
        for fb in self.fireballs:
            fb.draw()

        if self.sword is None:
            return
        self.sword.draw()
