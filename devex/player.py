import typing as t

import pygame

from .bars import EnergyBar, HealthBar
from .bloom import Bloom
from .player_attacks import EAttack, FireballManager, QAttack, WAttack
from .shared import Shared
from .utils import Animation, aura_load, load_scale_3


class Player:
    MAX_HEALTH = 180
    MAX_ENERGY = 100
    FRAMES = tuple(aura_load(f"assets/boost-aura-{n}.png") for n in range(1, 4))

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
        self.health = self.MAX_HEALTH
        self.mana = 0
        self.health_bar = HealthBar()
        self.energy_bar = EnergyBar()
        self.health_target_vector = pygame.Vector2(self.health, 0)
        self.mana_target_vector = pygame.Vector2(self.mana, 0)
        self.health_vector = pygame.Vector2(self.health, 0)
        self.mana_vector = pygame.Vector2(self.mana, 0)

        self.bar_anim_speed = 3
        self.mana_anim_speed = 3

        self.q_attack = QAttack()
        self.w_attack = WAttack()
        self.e_attack = EAttack()

        self.on_boost = False
        self.anim_boost = Animation(self.FRAMES, 0.1)
        self.boost_rect = self.FRAMES[0].get_rect()
        self.boost_timer = None

    def modify_health(self, term: int):
        if self.w_attack.active:
            return
        self.health_target_vector.x += term

    def modify_mana(self, term: int):
        self.mana_target_vector.x += term
        if self.mana_target_vector.x > self.MAX_ENERGY:
            self.mana_target_vector.x = self.MAX_ENERGY

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

    def update_boost_timer(self):
        if self.boost_timer is not None and self.boost_timer.tick():
            self.boost_timer = None
            self.on_boost = False

    def move_towards_health(self):
        self.bar_anim_speed += 3.3
        self.health_vector.move_towards_ip(
            self.health_target_vector, self.bar_anim_speed * self.shared.dt
        )
        self.health = self.health_vector.x

        if self.health_vector == self.health_target_vector:
            self.bar_anim_speed = 3

    def move_towards_mana(self):
        self.mana_anim_speed += 3.3
        self.mana_vector.move_towards_ip(
            self.mana_target_vector, self.mana_anim_speed * self.shared.dt
        )
        self.mana = self.mana_vector.x

        if self.mana_vector == self.mana_target_vector:
            self.mana_anim_speed = 3

    def update_boost(self):
        self.update_boost_timer()
        self.boost_rect.midbottom = self.rect.midbottom
        if self.on_boost:
            self.anim_boost.update()

    def update(self):
        self.anim.update()
        self.update_boost()

        self.follow_target()
        self.update_bloom()
        self.on_fly()
        self.on_shoot()
        self.health_bar.update()
        self.energy_bar.update()
        self.move_towards_health()
        self.move_towards_mana()
        self.q_attack.update()
        self.w_attack.update()
        self.e_attack.update()

    def draw(self):
        self.shared.screen.blit(
            self.anim.current_frame, self.shared.camera.transform(self.rect)
        )
        self.bloom.draw(self.shared.overlay)
        self.fireball_manager.draw()

        self.q_attack.draw()
        self.w_attack.draw()
        self.e_attack.draw()

        if not self.e_attack.active and self.on_boost:
            self.shared.screen.blit(
                self.anim_boost.current_frame,
                self.shared.camera.transform(self.boost_rect),
            )
