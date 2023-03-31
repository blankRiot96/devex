import itertools
import time

import pygame

from .shared import Shared
from .state_enums import State
from .utils import Time, get_font, render_at
from .widgets import Widgets


class PreviewLastGame:
    def __init__(self) -> None:
        self.shared = Shared()
        self.overlay = pygame.Surface(Shared.SCRECT.size)

        self.pics: list[pygame.Surface] = itertools.cycle(self.shared.gameplay_pics)
        try:
            self.current_pic = next(self.pics)
        except:
            self.current_pic = pygame.Surface(Shared.SCRECT.size)
        self.timer = Time(5.0)

    def update(self):
        if self.timer.tick():
            try:
                self.current_pic = next(self.pics)
            except:
                self.current_pic = pygame.Surface(Shared.SCRECT.size)

    def draw(self):
        self.shared.screen.blit(pygame.transform.grayscale(self.current_pic), (0, 0))


class GameOverState:
    REQUIRED_FIELDS = ["screen", "start_time", "gameplay_pics"]

    def __init__(self) -> None:
        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.next_state = None
        self.shared = Shared()
        self.clean_shared_data()
        self.shared.widgets = Widgets(style="gameover")
        self.preview = PreviewLastGame()
        self.font = get_font("assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 32)
        self.big_font = get_font(
            "assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 64
        )
        self.game_over_surf = self.big_font.render("<GAME OVER>", True, "red")

        lasted = int(time.time() - self.shared.start_time)
        minutes = lasted // 60
        seconds = lasted - (minutes * 60)
        seconds = int(seconds)
        self.lasted_surf = self.font.render(
            f"You lasted {minutes}m {seconds}s",
            True,
            "red",
        )
        self.message_surf = self.font.render(
            "Press ENTER to go to the main menu", True, "red"
        )

    def clean_shared_data(self):
        for field in dir(self.shared):
            if field in self.REQUIRED_FIELDS or field in Shared.__dict__:
                continue
            if field.startswith("__"):
                continue
            del self.shared.__dict__[field]

    def update(self):
        self.shared.widgets.update()

        for event in self.shared.events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.next_state = State.MENU

        self.preview.update()

    def draw(self):
        self.preview.draw()
        self.shared.widgets.draw()
        render_at(self.shared.screen, self.game_over_surf, "center", (0, -50))
        render_at(self.shared.screen, self.lasted_surf, "center", (0, 0))
        render_at(self.shared.screen, self.message_surf, "center", (0, 50))
