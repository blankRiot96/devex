import math
import time
import typing as t

import pygame
from logit import log

from .bloom import Bloom
from .cursor import CursorState
from .shared import Shared
from .utils import Animation, Projectile, Time, TimeOnce, get_font, load_scale_3


class Fireball(Projectile):
    INITIAL_SPEED = 600
    FRAMES = tuple(load_scale_3(f"assets/fireball-anim-{n}.png") for n in range(1, 4))
    EXPLOSION_FRAMES = tuple(
        load_scale_3(f"assets/explosion-{n}.png") for n in range(1, 8)
    )

    def __init__(self, radians: float, pos: t.Sequence) -> None:
        super().__init__(radians, Fireball.INITIAL_SPEED)
        self.pos = pygame.Vector2(pos)
        self.deceleration = 200
        self.damage = 60

        self.bloom = Bloom(0.3, wave_speed=0.01, expansion_factor=10)
        self.frames = tuple(
            pygame.transform.rotate(frame, math.degrees(-self.radians))
            for frame in Fireball.FRAMES
        )
        self.anim = Animation(self.frames, 0.2)
        self.rect = Fireball.FRAMES[0].get_rect()
        self.alive = True
        self.shared = Shared()

    def update(self):
        self.anim.update()
        self.bloom.update(self.shared.camera.transform(self.pos))
        self.get_delta_velocity(self.shared.dt)
        self.pos += self.dv
        self.speed -= self.deceleration * self.shared.dt
        self.rect.center = self.pos

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
    MAX_FIREBALLS = 10

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
        self.accel = 1500
        self.shared = Shared()
        self.pos = pos.copy()
        self.done = False

    def update(self):
        self.radius += self.expansion_speed * self.shared.dt
        if self.expansion_speed > 25:
            self.expansion_speed -= self.accel * self.shared.dt

        if self.radius > (HotBall.RANGE / 2):
            self.done = True

    def draw(self):
        pygame.draw.circle(
            self.shared.screen,
            "blue",
            self.shared.camera.transform(self.pos),
            self.radius,
            width=5,
        )


class AttackInfo:
    IMAGES = {
        pygame.K_q: [
            pygame.image.load("assets/q_attack.png").convert_alpha(),
            pygame.image.load("assets/q_attack_cooldown.png").convert_alpha(),
        ]
    }
    FONT = get_font("assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 32)

    def __init__(
        self,
        cooldown: float,
        pos: pygame.Vector2,
        attack_key: int,
        gold_to_unlock: int = 3,
        gold_to_upgrade: int = 1,
    ) -> None:
        self.shared = Shared()
        self.level = 1
        self.cooldown = TimeOnce(cooldown)
        self.attack_key = attack_key
        self.gold_to_unlock = gold_to_unlock
        self.gold_to_upgrade = gold_to_upgrade
        self.pos = pos.copy()
        self.usable = True
        self.using = False
        self.used = False

        self.logo_surf = self.IMAGES.get(attack_key)[0]
        self.logo_rect = self.logo_surf.get_rect(topleft=self.pos)

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
            ):
                self.using = True

    def on_using(self):
        self.cooldown.reset()
        self.usable = False
        self.using = False
        self.used = True

    def update(self):
        self.check_usable()
        self.check_using()
        if self.using:
            self.on_using()

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


class QAttack:
    """Extra hot fireball"""

    def __init__(self) -> None:
        self.shared = Shared()
        self.hotball = None
        self.active = False
        self.fireballs: list[Fireball] = []
        self.attack_info = AttackInfo(
            3.0,
            pos=pygame.Vector2(
                (Shared.SCREEN_WIDTH // 2) - 120, Shared.SCREEN_HEIGHT - 150
            ),
            attack_key=pygame.K_q,
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

    ...


class EAttack:
    """N fireballs in circular motion"""

    ...
