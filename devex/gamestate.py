import time

import pygame

from .camera import Camera
from .cursor import Cursor
from .platform import PlatformManager
from .player import Player
from .shared import Shared
from .ss_manager import ScreenShakeManager
from .state_enums import State
from .utils import Time
from .widgets import MessageLogWidget, Widgets


class GameState:
    def __init__(self) -> None:
        self.shared = Shared(
            camera=Camera(),
            current_program=None,
            collected_programs=[],
            gold=4,
            pyrite=0,
            final_boss=None,
            messages=MessageLogWidget.MESSAGES,
        )
        self.shared.messages.append("-- GAME SESSION STARTED --")
        self.shared.widgets = Widgets()
        self.next_state = None
        self.screen_shake_manager = ScreenShakeManager()
        self.origin = pygame.Vector2(100, 150)
        self.plat = PlatformManager()
        self.player = Player(self.origin)
        self.shared.player = self.player
        self.shared.overlay = self.shared.screen.copy()
        self.shared.overlay.fill("black")
        self.shared.overlay.set_alpha(150)
        self.shared.provisional_chunk = self.shared.screen.copy()
        self.shared.play_it_once_anims = []
        self.shared.cursor = Cursor()

        # Info for game over/victory state
        self.shared.start_time = time.time()
        self.shared.gameplay_pics: list[pygame.Surface] = []
        self.pic_timer = Time(3.0)

    def update_anims(self):
        for anim in self.shared.play_it_once_anims[:]:
            anim.update()

            if anim.done:
                self.shared.play_it_once_anims.remove(anim)

    def update(self):
        self.shared.camera.attach_to_player()
        self.plat.update()
        self.player.update()
        self.screen_shake_manager.update()
        self.update_anims()

        if self.shared.final_boss is not None and self.plat.done:
            self.shared.final_boss.update()

        self.shared.widgets.update()
        self.shared.cursor.update()

        self.on_player_death()
        self.on_victory()

    def draw_before_overlay(self):
        self.shared.overlay.fill("black")
        self.plat.draw()

    def draw_on_overlay(self):
        self.player.draw()
        self.plat.draw_torches()
        self.plat.draw_programs()
        if self.shared.final_boss is None:
            self.shared.screen.blit(
                self.shared.overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MIN
            )

    def draw_after_overlay(self):
        self.player.health_bar.draw()
        self.player.energy_bar.draw()
        self.player.q_attack.draw_front()
        self.player.w_attack.draw_front()
        self.player.e_attack.draw_front()
        self.draw_once_anims()

    def draw_once_anims(self):
        for anim in self.shared.play_it_once_anims:
            if hasattr(anim, "draw"):
                anim.draw()
                continue
            self.shared.screen.blit(
                anim.current_frame, self.shared.camera.transform(anim.pos)
            )

    def draw_final_boss(self):
        if self.shared.final_boss is not None and self.plat.done:
            self.shared.final_boss.draw()

    def on_player_death(self):
        if self.player.health <= 0:
            self.next_state = State.GAME_OVER

    def on_victory(self):
        if self.shared.final_boss is None:
            return
        if self.shared.final_boss.health <= 0:
            self.next_state = State.VICTORY

    def update_pics_capture(self):
        if self.pic_timer.tick():
            self.shared.gameplay_pics.append(self.shared.screen.copy())

            if len(self.shared.gameplay_pics) > 8:
                self.shared.gameplay_pics.pop(0)

    def draw(self):
        self.draw_before_overlay()
        if self.plat.done:
            self.draw_on_overlay()
        self.draw_final_boss()
        self.draw_after_overlay()
        self.shared.widgets.draw()
        self.shared.cursor.draw()
        self.update_pics_capture()
