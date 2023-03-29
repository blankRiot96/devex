from __future__ import annotations

import itertools
import math
import time
import typing as t

import pygame
from logit import log

from .bloom import Bloom
from .cursor import CursorState
from .shared import Shared
from .utils import (
    Animation,
    Projectile,
    Time,
    TimeOnce,
    aura_load,
    get_font,
    load_scale_3,
)


class Fireball(Projectile):
    INITIAL_SPEED = 600
    FRAMES = tuple(load_scale_3(f"assets/fireball-anim-{n}.png") for n in range(1, 4))
    EXPLOSION_FRAMES = tuple(
        load_scale_3(f"assets/explosion-{n}.png") for n in range(1, 8)
    )

    def __init__(
        self,
        radians: float,
        pos: t.Sequence,
        damage: int = 60,
        speed: None | float = None,
    ) -> None:
        if speed is None:
            speed = self.INITIAL_SPEED

        super().__init__(radians, speed)
        self.pos = pygame.Vector2(pos)
        self.deceleration = 200
        self.damage = damage

        self.bloom = Bloom(0.3, wave_speed=0.01, expansion_factor=10)
        self.frames = tuple(
            pygame.transform.rotate(frame, math.degrees(-self.radians))
            for frame in self.FRAMES
        )
        self.anim = Animation(self.frames, 0.2)
        self.rect = self.FRAMES[0].get_rect()
        self.alive = True
        self.shared = Shared()

    def update(self):
        self.get_delta_velocity(self.shared.dt)
        self.pos += self.dv
        self.speed -= self.deceleration * self.shared.dt
        self.rect.center = self.pos
        self.anim.update()
        self.bloom.update(self.shared.camera.transform(self.pos))

        if self.speed < 100:
            self.alive = False

    def draw(self):
        self.shared.screen.blit(
            self.anim.current_frame, self.shared.camera.transform(self.rect)
        )
        self.bloom.draw(self.shared.overlay)


class FireballManager:
    def __init__(self) -> None:
        self.fireballs: set[Fireball] = set()
        self.shared = Shared()
        self.cooldown = Time(0.6)
        self.creatable = True

    def on_create(self):
        if self.shared.cursor.state != CursorState.ATTACK:
            return

        if not self.creatable:
            if self.cooldown.tick():
                self.creatable = True
        for event in self.shared.events:
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.creatable
            ):
                self.fireballs.add(
                    Fireball(
                        self.shared.cursor.radians_between_player,
                        self.shared.player.pos,
                    )
                )
                self.creatable = False
                self.cooldown.reset()

    def retain_active_fireballs(self):
        for fireball in set(self.fireballs):
            if not fireball.alive:
                self.fireballs.remove(fireball)

    def update(self):
        self.on_create()
        self.retain_active_fireballs()

        for fireball in self.fireballs:
            fireball.update()

    def draw(self):
        for fireball in self.fireballs:
            fireball.draw()


class HotBall(Projectile):
    INITIAL_SPEED = 400
    FRAMES = tuple(load_scale_3(f"assets/hotball-{n}.png") for n in range(1, 6))
    EXPLOSION_FRAMES = tuple(
        load_scale_3(f"assets/explosion-{n}.png") for n in range(1, 8)
    )
    RANGE = 500
    INITIAL_MAX_FIREBALLS = 10
    MAX_FIREBALLS = INITIAL_MAX_FIREBALLS

    def __init__(self, radians: float, pos: t.Sequence) -> None:
        super().__init__(radians, HotBall.INITIAL_SPEED)
        self.shared = Shared()
        self.pos = pygame.Vector2(pos)
        self.deceleration = 200
        self.damage = 60
        self.target = self.shared.cursor.trans_pos.copy()

        self.bloom = Bloom(0.3, wave_speed=0.01, expansion_factor=10)
        self.frames = tuple(
            pygame.transform.rotate(frame, math.degrees(-self.radians))
            for frame in HotBall.FRAMES
        )
        self.anim = Animation(self.frames, 0.2)
        self.rect = HotBall.FRAMES[0].get_rect()
        self.alive = True

    def project(self):
        self.anim.update()
        self.bloom.update(self.shared.camera.transform(self.pos))
        self.pos.move_towards_ip(self.target, self.speed * self.shared.dt)
        self.rect.center = self.pos

    def on_boom(self):
        if self.pos == self.target:
            self.alive = False
            self.shared.ss.add(2.0, 3.0)
            self.shared.play_it_once_anims.append(OnBoomAnimation(self.pos))

    def update(self):
        self.project()
        self.on_boom()

    def draw(self):
        self.shared.screen.blit(
            self.anim.current_frame, self.shared.camera.transform(self.rect)
        )
        self.bloom.draw(self.shared.overlay)


class OnBoomAnimation:
    def __init__(self, pos) -> None:
        self.radius = 0
        self.expansion_speed = 1000
        self.accel = 1000
        self.shared = Shared()
        self.pos = pos.copy()
        self.done = False

    def update(self):
        self.radius += self.expansion_speed * self.shared.dt
        if self.expansion_speed > 25:
            self.expansion_speed -= self.accel * self.shared.dt

        if self.radius > HotBall.RANGE:
            self.done = True

    def draw(self):
        pygame.draw.circle(
            self.shared.screen,
            "blue",
            self.shared.camera.transform(self.pos),
            self.radius,
            width=5,
        )


class LevelUpButton:
    IMAGE = pygame.image.load("assets/lvl-up.png").convert_alpha()

    def __init__(self, attack_info: AttackInfo) -> None:
        self.ai = attack_info
        self.image = self.IMAGE.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (
            self.ai.logo_rect.centerx,
            self.ai.logo_rect.centery - 80,
        )
        self.shared = Shared()

    def has_enough_gold(self):
        if self.ai.level == 0:
            return self.shared.gold >= self.ai.gold_to_unlock
        return self.shared.gold >= self.ai.gold_to_upgrade

    def level_not_max(self):
        return self.ai.level < self.ai.max_level

    def hovering(self):
        return self.rect.collidepoint(self.shared.cursor.pos)

    def clicked(self):
        return self.shared.cursor.clicked

    def update(self):
        if (
            self.has_enough_gold()
            and self.level_not_max()
            and self.hovering()
            and self.clicked()
        ):
            if self.ai.level == 0:
                self.shared.gold -= self.ai.gold_to_unlock
            else:
                self.shared.gold -= self.ai.gold_to_upgrade
            self.ai.level += 1
            self.shared.widgets.construct_widgets()

        if self.has_enough_gold():
            self.image.set_alpha(255)
        else:
            self.image.set_alpha(150)

    def draw(self):
        self.shared.screen.blit(self.image, self.rect)


class AttackInfo:
    IMAGES = {
        pygame.K_q: [
            pygame.image.load("assets/q_attack.png").convert_alpha(),
            pygame.image.load("assets/q_attack_cooldown.png").convert_alpha(),
        ],
        pygame.K_w: [
            pygame.image.load("assets/w_attack.png").convert_alpha(),
            pygame.image.load("assets/w_attack_cooldown.png").convert_alpha(),
        ],
        pygame.K_e: [
            pygame.image.load("assets/e_attack.png").convert_alpha(),
            pygame.image.load("assets/e_attack_cooldown.png").convert_alpha(),
        ],
    }
    FONT = get_font("assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 32)
    LEVEL_FONT = get_font("assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 16)

    def __init__(
        self,
        cooldown: float,
        attack_key: int,
        mana_cost: int,
        gold_to_unlock: int = 4,
        gold_to_upgrade: int = 1,
        max_level: int = 10,
    ) -> None:
        self.shared = Shared()
        self.level = 0
        self.cooldown = TimeOnce(cooldown)
        self.attack_key = attack_key
        self.mana_cost = mana_cost
        self.gold_to_unlock = gold_to_unlock
        self.gold_to_upgrade = gold_to_upgrade
        self.max_level = max_level
        self.get_pos()
        self.usable = True
        self.using = False
        self.used = False

        self.logo_surf = self.IMAGES.get(attack_key)[0]
        self.logo_rect = self.logo_surf.get_rect(topleft=self.pos)
        self.lvl_up_btn = LevelUpButton(self)

    def get_pos(self):
        logo_size = 100
        padding = 20
        y = Shared.SCREEN_HEIGHT - 200
        mid = Shared.SCRECT.midbottom
        if self.attack_key == pygame.K_q:
            x = mid[0] - (logo_size / 2) - logo_size - padding
        elif self.attack_key == pygame.K_w:
            x = mid[0] - (logo_size / 2)
        elif self.attack_key == pygame.K_e:
            x = mid[0] - (logo_size / 2) + logo_size + padding

        self.pos = pygame.Vector2(x, y)

    def check_usable(self):
        if self.cooldown.tick() and self.level > 0:
            self.usable = True

    def check_using(self):
        self.using = False
        for event in self.shared.events:
            if (
                event.type == pygame.KEYDOWN
                and event.key == self.attack_key
                and self.usable
                and self.shared.player.mana >= self.mana_cost
            ):
                self.using = True

    def on_using(self):
        self.cooldown.reset()
        self.usable = False
        self.using = False
        self.used = True
        self.shared.player.modify_mana(-self.mana_cost)

    def update(self):
        self.lvl_up_btn.update()
        if self.level == 0:
            return
        self.check_usable()
        self.check_using()
        if self.using:
            self.on_using()

    def render_level(self):
        if self.level == self.max_level:
            text = "Lvl: MAX"
        else:
            text = f"Lvl: {self.level}"
        level_surf = self.LEVEL_FONT.render(text, True, "green")
        level_rect = level_surf.get_rect()
        level_rect.center = (
            self.logo_rect.centerx,
            self.logo_rect.centery + 60,
        )
        self.shared.screen.blit(level_surf, level_rect)
        self.lvl_up_btn.draw()

    def render_cooldown(self):
        self.logo_surf = self.IMAGES.get(self.attack_key)[1]
        font_text = time.perf_counter() - self.cooldown.start
        font_text = self.cooldown.time_to_pass - font_text
        if font_text > 1:
            font_text = f"{font_text:.0f}"
        else:
            font_text = f"{font_text:.1f}"
        font_surf = self.FONT.render(font_text, True, "white")
        font_rect = font_surf.get_rect(center=self.logo_rect.center)

        self.shared.screen.blit(font_surf, font_rect)

    def draw(self):
        self.shared.screen.blit(self.logo_surf, self.logo_rect)
        if self.level > 0 and not self.cooldown.tick() and not self.usable:
            self.render_cooldown()
        else:
            self.logo_surf = self.IMAGES.get(self.attack_key)[0]
        self.render_level()


class QAttack:
    """Extra hot fireball"""

    def __init__(self) -> None:
        self.shared = Shared()
        self.hotball = None
        self.active = False
        self.fireballs: list[Fireball] = []
        self.attack_info = AttackInfo(
            3.0, attack_key=pygame.K_q, gold_to_unlock=6, mana_cost=60
        )

    def add_fireball(self, enemy):
        self.attack_info.used = False
        self.shared.player.fireball_manager.fireballs.add(
            Fireball(
                math.atan2(
                    enemy.pos.y - self.hotball.pos.y,
                    enemy.pos.x - self.hotball.pos.x,
                ),
                enemy.pos,
            )
        )

    def blast_surrounding_enemies(self, added=0):
        for plat in self.shared.current_chunks:
            for enemy in plat.enemies:
                if enemy.pos.distance_to(self.hotball.pos) <= HotBall.RANGE:
                    if added > HotBall.MAX_FIREBALLS:
                        self.active = False
                        self.hotball = None
                        return
                    self.add_fireball(enemy)
                    added += 1

        if (
            self.shared.final_boss is not None
            and self.shared.final_boss.pos.distance_to(self.hotball.pos)
            <= HotBall.RANGE
        ):
            self.add_fireball(self.shared.final_boss)
            added += 1

        if added == 0:
            return
        if added < HotBall.MAX_FIREBALLS:
            self.blast_surrounding_enemies(added)

    def on_active(self):
        if self.hotball is None:
            self.hotball = HotBall(
                self.shared.cursor.radians_between_player,
                self.shared.player.pos,
            )

        self.hotball.update()

        if not self.hotball.alive:
            self.blast_surrounding_enemies()
            self.hotball = None
            self.active = False

    def get_left_click(self):
        for event in self.shared.events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return True
        return False

    def on_deactive(self):
        if self.attack_info.used and self.get_left_click():
            self.active = True

    def update_level(self):
        HotBall.MAX_FIREBALLS = HotBall.INITIAL_MAX_FIREBALLS + self.attack_info.level

    def update(self):
        self.attack_info.update()
        if self.active:
            self.on_active()
        else:
            self.on_deactive()

    def draw(self):
        if self.active and self.hotball is not None:
            self.hotball.draw()

    def draw_front(self):
        self.attack_info.draw()


class WAttack:
    """Immunity for x seconds"""

    FRAMES = tuple(aura_load(f"assets/immunity-aura-{n}.png") for n in range(1, 4))
    SHIELD = load_scale_3("assets/shield.png")

    def __init__(self) -> None:
        self.shared = Shared()
        self.active = False
        self.initial_cd = 30.0
        self.attack_info = AttackInfo(
            self.initial_cd, attack_key=pygame.K_w, gold_to_unlock=3, mana_cost=15
        )
        self.registered_health = 0
        self.anim = Animation(self.FRAMES, 0.1)
        self.rect = self.FRAMES[0].get_rect()
        self.initial_attack_cd = 6.0
        self.cooldown = TimeOnce(self.initial_attack_cd)

        self.shield_rect = self.SHIELD.get_rect()

    def on_active(self):
        if self.cooldown.tick():
            self.active = False
            self.attack_info.used = False
            return

        self.shared.player.modify_health(
            self.registered_health - self.shared.player.health
        )
        self.rect.midbottom = self.shared.player.rect.midbottom
        self.anim.update()

        self.shield_rect.center = (
            self.shared.player.rect.centerx,
            self.shared.player.rect.centery - 60,
        )

    def on_deactive(self):
        if self.attack_info.used:
            self.active = True
            self.registered_health = self.shared.player.health
            self.cooldown.reset()

    def update_level(self):
        self.attack_info.cooldown.time_to_pass = self.initial_cd - (
            self.attack_info.level / 2
        )
        self.cooldown.time_to_pass = self.initial_attack_cd + self.attack_info.level

    def update(self):
        self.attack_info.update()
        self.update_level()
        if self.active:
            self.on_active()
        else:
            self.on_deactive()

    def draw(self):
        if self.active:
            self.shared.screen.blit(
                self.anim.current_frame,
                self.shared.camera.transform(self.rect),
            )
            self.shared.screen.blit(
                self.SHIELD, self.shared.camera.transform(self.shield_rect)
            )

    def draw_front(self):
        self.attack_info.draw()


class SpiralFireball(Fireball):
    FRAMES = tuple(load_scale_3(f"assets/spiralball-anim-{n}.png") for n in range(1, 5))

    def __init__(self, radians: float | int) -> None:
        super().__init__(radians, pygame.Vector2())
        self.angular_velocity = 0.07

    def update(self, radius):
        self.radians += 0.02
        self.pos.x = self.shared.player.rect.centerx + radius * math.cos(self.radians)
        self.pos.y = self.shared.player.rect.centery + radius * math.sin(self.radians)

        self.rect.center = self.pos
        self.anim.update()
        self.bloom.update(self.shared.camera.transform(self.pos))


class EAttack:
    """N fireballs in circular motion"""

    STARTER_BALLS = 4
    MAX_RADIUS = 500

    def __init__(self) -> None:
        self.shared = Shared()
        self.active = False
        self.attack_info = AttackInfo(7.0, attack_key=pygame.K_e, mana_cost=40)
        self.cooldown = TimeOnce(6.0)
        self.fireballs: list[SpiralFireball] = []
        self.n_balls = self.STARTER_BALLS
        self.radius = 200

    def gen_fireballs(self):
        for n in range(self.n_balls):
            radians = 2 * math.pi * n / self.n_balls
            self.fireballs.append(SpiralFireball(radians))

    def on_active(self):
        if self.cooldown.tick():
            self.active = False
            self.attack_info.used = False
            self.fireballs.clear()
            return

        self.update_radius()
        for fireball in self.fireballs[:]:
            fireball.update(self.radius)
            if not fireball.alive:
                self.fireballs.remove(fireball)

    def on_deactive(self):
        if self.attack_info.used:
            self.active = True
            self.cooldown.reset()
            self.gen_fireballs()

    def update_level(self):
        self.n_balls = self.STARTER_BALLS + self.attack_info.level

    def update_radius(self):
        for event in self.shared.events:
            if event.type == pygame.MOUSEWHEEL:
                self.radius += event.precise_y * 20
                if self.radius > self.MAX_RADIUS:
                    self.radius = self.MAX_RADIUS

    def update(self):
        self.attack_info.update()
        self.update_level()
        if self.active:
            self.on_active()
        else:
            self.on_deactive()

    def draw(self):
        if self.active:
            for fireball in self.fireballs:
                fireball.draw()

    def draw_front(self):
        self.attack_info.draw()
