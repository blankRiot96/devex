import itertools

import pygame

from .shared import Shared
from .state_enums import State
from .utils import SinWave, get_font, render_at, scale_by
from .widgets import Widgets


class BackgroundRender:
    def __init__(self) -> None:
        self.shared = Shared()
        self.original_provs = itertools.cycle(
            (
                pygame.image.load("assets/prov.png").convert(),
                pygame.image.load("assets/prov_2.png").convert(),
            )
        )
        self.original_prov = next(self.original_provs)
        self.prov = self.original_prov.copy()
        self.zoom = 1
        self.zoom_rate = 0.08
        self.alpha = 1
        self.alpha_rate = 25
        self.sign = 1

    def update(self):
        self.zoom = (self.alpha / 255) / 2
        self.alpha += (self.alpha_rate * self.shared.dt) * self.sign
        if self.alpha >= 255 or self.alpha <= 0:
            self.sign *= -1
            self.original_prov = next(self.original_provs)

        if self.zoom > 1.5:
            self.zoom = 1
        self.prov = scale_by(self.original_prov, 1 + self.zoom)
        self.prov.set_alpha(self.alpha)

    def draw(self):
        render_at(self.shared.screen, self.prov, "center")


class DashBoardRender:
    def __init__(self) -> None:
        self.image = pygame.image.load("assets/dashboard.png").convert_alpha()
        self.shared = Shared()
        self.y = 0
        self.wave = SinWave(0.07)
        self.font = get_font("assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 32)
        self.options_surf = self.font.render(
            """ <Press ENTER to start>
<Press [T] for tutorial>""",
            True,
            "yellow",
        )

    def update(self):
        self.y = self.wave.val() * 15

    def draw(self):
        render_at(self.shared.screen, self.image, "center", (0, -100 + self.y))
        render_at(self.shared.screen, self.options_surf, "center", (0, 100))


class MenuState:
    REQUIRED_FIELDS = ["screen"]

    def __init__(self) -> None:
        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.next_state = None
        self.shared = Shared()
        self.clean_shared_data()
        self.shared.widgets = Widgets(style="gameover")
        self.bg = BackgroundRender()
        self.dash = DashBoardRender()

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
                self.next_state = State.GAME

        self.bg.update()
        self.dash.update()

    def draw(self):
        self.bg.draw()
        self.dash.draw()
        self.shared.widgets.draw()
