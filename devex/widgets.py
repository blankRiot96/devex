from typing import Protocol, Sequence
import pygame
from .utils import get_font, render_at
from .shared import Shared
from logit import log


class Widget(Protocol):
    def __init__(self, pos: Sequence) -> None:
        super().__init__()

    def update(self) -> None:
        ...

    def draw(self) -> None:
        ...


class Widgets:
    def __init__(self) -> None:
        self.widgets: list[Widget] = []

    def add(self, widget: Widget, pos: Sequence):
        self.widgets.append(widget(pos))

    def remove(self, widget: Widget):
        self.widgets.remove(widget)

    def update(self):
        for widget in self.widgets:
            widget.update()

    def draw(self):
        for widget in self.widgets:
            widget.draw()


class QuitWidget:
    def __init__(self, pos: Sequence) -> None:
        self.shared = Shared()
        self.pos = pygame.Vector2(pos)
        self.surface = pygame.Surface((500, 300))
        self.surface.set_alpha(150)
        self.font = get_font("assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 25)
        self.fill_font()

    def fill_font(self):
        font_surf = self.font.render(
            "Do you really want to quit?\n\n"
            "Quit: Press ESC again\n"
            "Ignore: Press ENTER\n",
            True,
            "white",
        )
        render_at(self.surface, font_surf, "center")

    def update(self):
        for event in self.shared.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit
                elif event.key == pygame.K_RETURN:
                    self.shared.widgets.remove(self)

    def draw(self):
        render_at(self.shared.screen, self.surface, "center")
