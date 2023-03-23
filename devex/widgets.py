import inspect
from dataclasses import dataclass, field
from typing import MutableSequence, Protocol, Sequence

import pygame
from logit import log

from . import game_funcs
from .enemies import BeeList, CentiSet, HumanStr, PoopyBytes, PotatoInt
from .shared import Shared
from .utils import get_font, render_at, scale_by


class Widget(Protocol):
    def __init__(self, pos: Sequence) -> None:
        super().__init__()

    def update(self) -> None:
        ...

    def draw(self) -> None:
        ...


@dataclass
class Scrollable:
    surf: pygame.Surface
    pos: pygame.Vector2 = field(default_factory=pygame.Vector2)

    def __post_init__(self):
        self.original_pos = self.pos.copy()


class VerticalScrollBar:
    def __init__(
        self, surf: pygame.Surface, pos: Sequence, width: int, height: int, padding: int
    ) -> None:
        self.shared = Shared()
        self.surf = surf
        self.pos = pygame.Vector2(pos)
        self.rect = self.surf.get_rect(topleft=self.pos)
        self.padding = padding
        self.scrollables: list[Scrollable] = []
        self.scroll_rect = pygame.Rect(0, 0, width, height)
        self.scroll_pos = pygame.Vector2()
        self.scroll_surf = pygame.Surface(self.scroll_rect.size)
        self.scroll_surf.fill("grey")
        self.max_scroll_height = self.surf.get_height() - self.scroll_rect.height
        self.ratio = 0
        self.vertical_taken = 0
        self.selected = False
        self.first_register = True
        self.registered_pos = None
        self.registered_scroll_pos = None

    def add(self, scrollable: Scrollable) -> None:
        scrollable.pos = pygame.Vector2(
            self.scroll_rect.width + 10,
            self.vertical_taken + self.padding + scrollable.surf.get_height(),
        )
        scrollable.original_pos = scrollable.pos.copy()
        self.vertical_taken = scrollable.pos.y
        self.scrollables.append(scrollable)

    def on_drag_scrollbar(self):
        if self.scroll_rect.move(0, self.pos.y).collidepoint(self.shared.cursor.pos):
            self.scroll_surf.fill((30, 30, 30))
            self.selected = True
        else:
            self.scroll_surf.fill("grey")
            self.selected = False
            return

        if self.shared.mouse_press[0]:
            if self.first_register:
                self.registered_pos = self.shared.cursor.pos
                self.registered_scroll_pos = self.scroll_pos.copy()
                self.first_register = False

            self.scroll_pos.y = self.registered_scroll_pos.y
            self.scroll_pos.y += self.shared.cursor.pos[1] - self.registered_pos[1]
        else:
            self.first_register = True

    def update(self):
        self.on_drag_scrollbar()
        self.scroll_rect.topleft = self.scroll_pos
        self.ratio = self.scroll_pos.y / self.max_scroll_height

        if len(self.scrollables) == 0:
            return
        self.scrollables[-1].pos.y = (1 - self.ratio) * self.scrollables[
            -1
        ].original_pos.y
        for scrollable in self.scrollables[:-1]:
            scrollable.pos.y = scrollable.original_pos.y
            scrollable.pos.y += (
                self.scrollables[-1].pos.y - self.scrollables[-1].original_pos.y
            )

    def draw(self):
        self.surf.blit(self.scroll_surf, self.scroll_pos)
        for scrollable in self.scrollables:
            self.surf.blit(scrollable.surf, scrollable.pos)


class Widgets:
    def __init__(self) -> None:
        self.shared = Shared(
            slots={PotatoInt: 0, HumanStr: 0, BeeList: 0, PoopyBytes: 0, CentiSet: 0}
        )
        self.widgets: list[Widget] = []
        self.preview_options: dict[int, list[Widget | str]] = {
            pygame.K_i: [InventoryWidget, "closed"],
            pygame.K_l: [MessageLogWidget, "closed"],
            pygame.K_p: [ProgramWidget, "closed"],
        }

    def add(self, widget: Widget, pos: Sequence):
        self.widgets.append(widget(pos))

    def remove(self, widget: Widget):
        self.widgets.remove(widget)

    def preview_widgets(self, event: pygame.event.Event):
        option = self.preview_options.get(event.key)
        if option is None:
            return

        if option[1] == "closed":
            option[1] = "open"
            self.shared.widgets.add(option[0], option[0].IDEAL_POS)
            return

        option[1] = "closed"
        for widget in self.widgets:
            if isinstance(widget, option[0]):
                self.widgets.remove(widget)
                return

    def handle_quit(self):
        for event in self.shared.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.shared.widgets.add(QuitWidget, (50, 50))

    def update(self):
        for event in self.shared.events:
            if event.type == pygame.KEYDOWN:
                self.preview_widgets(event)
        for widget in self.widgets:
            widget.update()

        self.handle_quit()

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


class InventoryWidget:
    SIZE = 600, 400
    IDEAL_POS = 0, 0
    FONT = get_font("assets/Hack/Hack Bold Nerd Font Complete Mono.ttf", 16)
    ITEM_SPACING = 20

    def __init__(self, pos) -> None:
        self.shared = Shared()
        self.surf = pygame.Surface(InventoryWidget.SIZE)
        self.surf.fill((60, 60, 60))
        self.surf.set_alpha(150)
        self.pos = pygame.Vector2(pos)
        self.filled_vertical_space = 0
        self.gen_image_slots()

    def gen_image_slots(self):
        title = self.FONT.render("Inventory", True, "white")
        self.surf.blit(title, (20, 10))
        self.filled_vertical_space += title.get_height() + 10
        index = 0
        for slot, quantity in self.shared.slots.items():
            surf = pygame.Surface((48, 48))
            surf.fill((40, 40, 40))
            if quantity > 0:
                surf.blit(slot.IMAGE, (0, 0))
                font_surf = self.FONT.render(str(quantity), True, "yellow")
                render_at(surf, font_surf, "bottomright")

            x = (surf.get_width() + InventoryWidget.ITEM_SPACING) * index
            x += InventoryWidget.ITEM_SPACING
            y = self.filled_vertical_space
            y += InventoryWidget.ITEM_SPACING
            self.surf.blit(surf, (x, y))

            index += 1

    def update(self):
        ...

    def draw(self):
        self.shared.screen.blit(self.surf, self.pos)


class MessageLogWidget:
    SIZE = 400, 400
    IDEAL_POS = Shared.SCRECT.bottomright - pygame.Vector2(SIZE)

    def __init__(self, pos) -> None:
        self.shared = Shared()
        self.surf = pygame.Surface(MessageLogWidget.SIZE)
        self.surf.fill((60, 60, 60))
        self.surf.set_alpha(150)
        self.pos = pygame.Vector2(pos)

    def update(self):
        ...

    def draw(self):
        self.shared.screen.blit(self.surf, self.pos)


class ProgramWidget:
    SIZE = InventoryWidget.SIZE[0], Shared.SCREEN_HEIGHT - InventoryWidget.SIZE[1] - 20
    IDEAL_POS = Shared.SCRECT.bottomleft - pygame.Vector2(0, SIZE[1])
    FONT = get_font("assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 25)

    def __init__(self, pos) -> None:
        self.surf = pygame.Surface(ProgramWidget.SIZE)
        self.surf.fill((60, 60, 60))
        self.surf.set_alpha(150)
        self.pos = pos
        self.shared = Shared()
        self.scroll_bar = VerticalScrollBar(self.surf, self.pos, 30, 100, 10)
        self.gen_elements()

    def gen_elements(self):
        if self.shared.current_program is None:
            self.gen_not_found()
            return

        self.gen_code_element()
        self.gen_arguments_element()
        self.gen_execute_element()

    def gen_not_found(self):
        self.scroll_bar.add(
            Scrollable(self.FONT.render("No program selected", True, "white"))
        )

    def gen_code_element(self):
        ...

    def gen_arguments_element(self):
        ...

    def gen_execute_element(self):
        ...

    def update(self):
        self.scroll_bar.update()

    def draw(self):
        self.surf.fill((60, 60, 60))
        self.scroll_bar.draw()
        self.shared.screen.blit(self.surf, self.pos)
