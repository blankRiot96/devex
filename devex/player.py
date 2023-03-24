import math
import typing as t

import pygame
from logit import log

from .bloom import Bloom
from .cursor import CursorState
from .shared import Shared
from .utils import Animation, Projectile, load_scale_3


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

    def on_create(self):
        if self.shared.cursor.state != CursorState.ATTACK:
            return
        for event in self.shared.events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.fireballs.add(
                    Fireball(
                        self.shared.cursor.radians_between_player,
                        self.shared.player.pos,
                    )
                )

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


class Player:
    def __init__(self, origin: pygame.Vector2) -> None:
        self.shared = Shared()
        self.pos = origin.copy()
        self.frames = [load_scale_3(f"assets/player-anim-{n}.png") for n in range(1, 7)]
        self.birby_frames = [
            load_scale_3(f"assets/player-birb-{n}.png") for n in range(1, 3)
        ]
        self.rect = self.frames[0].get_rect(midbottom=self.pos)
        self.idle_anim = Animation(self.frames, 0.3)
        self.bloom = Bloom(2, wave_speed=0.02, expansion_factor=70, v2=False)
        self.birb_anim = Animation(self.birby_frames, 0.3)
        self.anim = self.idle_anim
        self.fireball_manager = FireballManager()

    def follow_target(self):
        if self.shared.cursor.player_target is not None:
            self.pos.move_towards_ip(
                self.shared.cursor.player_target, 150 * self.shared.dt
            )

        self.rect.midbottom = self.pos

    def update_bloom(self):
        self.bloom.update(self.shared.camera.transform(self.rect.center))

    def on_fly(self):
        if (
            self.shared.provisional_chunk.get_at(
                tuple(map(int, self.shared.camera.transform(self.rect.midbottom)))
            )
            != self.shared.cursor.surface_color
        ):
            self.anim = self.birb_anim
        else:
            self.anim = self.idle_anim

    def on_shoot(self):
        self.fireball_manager.update()

    def update(self):
        self.anim.update()

        self.follow_target()
        self.update_bloom()
        self.on_fly()
        self.on_shoot()

    def draw(self):
        self.shared.screen.blit(
            self.anim.current_frame, self.shared.camera.transform(self.rect)
        )
        self.bloom.draw(self.shared.overlay)
        self.fireball_manager.draw()
