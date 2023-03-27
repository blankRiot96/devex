import pygame

from .camera import Camera
from .platform import PlatformManager
from .player import Player
from .shared import Shared
from .ss_manager import ScreenShakeManager


class GameState:
    def __init__(self) -> None:
        self.next_state = None
        self.shared = Shared(
            camera=Camera(),
            current_program=None,
            collected_programs=[],
            gold=0,
            pyrite=0,
        )
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

    def draw(self):
        self.shared.overlay.fill("black")
        self.plat.draw()
        if self.plat.done:
            self.player.draw()
            self.plat.draw_torches()
            self.plat.draw_programs()
            self.shared.screen.blit(
                self.shared.overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MIN
            )
        self.player.health_bar.draw()
        self.player.energy_bar.draw()

        for anim in self.shared.play_it_once_anims:
            self.shared.screen.blit(
                anim.current_frame, self.shared.camera.transform(anim.pos)
            )
