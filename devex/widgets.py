import random
from dataclasses import dataclass, field
from typing import Any, Protocol, Sequence

import pygame

from .camera import Camera
from .cursor import CursorState
from .enemies import BeeList, CentiSet, HumanStr, PoopyBytes, PotatoInt, ShroomDict
from .shared import Shared
from .utils import get_font, load_scale_3, render_at


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
            self.vertical_taken + self.padding,
        )
        scrollable.original_pos = scrollable.pos.copy()
        self.vertical_taken = scrollable.pos.y + scrollable.surf.get_height()
        self.scrollables.append(scrollable)

    def on_drag_scrollbar(self):
        if self.scroll_rect.move(self.pos.x, self.pos.y).collidepoint(
            self.shared.cursor.pos
        ):
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
    def __init__(self, style: str = "game") -> None:
        self.style = style
        if style == "game":
            self.init_game()
        elif style == "gameover":
            self.init_gameover()
        self.widgets: list[Widget] = []
        self.construct_widgets()

    def init_game(self):
        self.shared = Shared(
            values={
                PotatoInt: [],
                HumanStr: [],
                BeeList: [],
                PoopyBytes: [],
                CentiSet: [],
                ShroomDict: [],
            },
            inv_widget=None,
            prg_widget=None,
        )
        self.preview_options: dict[int, list[Widget | str]] = {
            pygame.K_i: [InventoryWidget, "closed"],
            pygame.K_l: [MessageLogWidget, "open"],
            pygame.K_p: [ProgramWidget, "closed"],
            pygame.K_m: [MiniMapWidget, "open"],
        }

    def init_gameover(self):
        self.shared = Shared()
        self.preview_options = {}

    def add(self, widget: Widget, pos: Sequence):
        if widget == InventoryWidget:
            w = widget(pos)
            self.shared.inv_widget = w
            self.widgets.append(w)
            return
        elif widget == ProgramWidget:
            w = widget(pos)
            self.shared.prg_widget = w
            self.widgets.append(w)
            return
        self.widgets.append(widget(pos))

    def remove(self, widget: Widget):
        if widget == InventoryWidget:
            self.inv_widget = None
        elif widget == ProgramWidget:
            self.prg_widget = None
        self.widgets.remove(widget)

    def remove_type(self, widget_type):
        for widget in self.widgets:
            if isinstance(widget, widget_type):
                self.widgets.remove(widget)
                return

    def preview_widgets(self, event_key: int):
        option = self.preview_options.get(event_key)
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

    def construct_widgets(self):
        self.widgets.clear()
        for option in self.preview_options.values():
            if option[1] == "open":
                self.add(option[0], option[0].IDEAL_POS)

    def handle_quit(self):
        for event in self.shared.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.shared.widgets.add(QuitWidget, (50, 50))

    def update(self):
        for event in self.shared.events:
            if event.type == pygame.KEYDOWN:
                self.preview_widgets(event.key)

        found = False
        for widget in self.widgets:
            widget.update()

            if self.style == "game":
                rect = widget.surf.get_rect(topleft=widget.pos)
                if rect.collidepoint(self.shared.cursor.pos):
                    self.shared.cursor.state = CursorState.USER_INTERFACE
                    found = True

        if self.style == "game":
            if not found:
                self.shared.cursor.state = CursorState.FORBIDDEN

        self.handle_quit()

    def draw(self):
        for widget in self.widgets:
            widget.draw()


class QuitWidget:
    def __init__(self, pos: Sequence) -> None:
        self.shared = Shared()
        self.pos = pygame.Vector2(pos)
        self.surf = pygame.Surface((500, 300))
        self.surf.set_alpha(150)
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
        render_at(self.surf, font_surf, "center")

    def update(self):
        for event in self.shared.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    # pygame.image.save(self.shared.provisional_chunk, "prov.png")
                    raise SystemExit
                elif event.key == pygame.K_RETURN:
                    self.shared.widgets.remove(self)

    def draw(self):
        render_at(self.shared.screen, self.surf, "center")


class InventoryWidget:
    SIZE = 600, 400
    IDEAL_POS = 0, 0
    FONT = get_font("assets/Hack/Hack Bold Nerd Font Complete Mono.ttf", 16)
    ITEM_SPACING = 20
    IMAGES = load_scale_3("assets/gold.png"), load_scale_3("assets/pyrite.png")

    def __init__(self, pos) -> None:
        self.shared = Shared()
        self.surf = pygame.Surface(InventoryWidget.SIZE)
        self.surf.set_alpha(150)
        self.pos = pygame.Vector2(pos)
        self.chosen_index = None
        self.conv_btn = ConvertButton()
        self.construct()

    def construct(self):
        self.filled_vertical_space = 0
        self.surf.fill((60, 60, 60))
        self.gen_inventory_slots()
        self.gen_mineral_slots()
        self.gen_code_slots()

    def gen_inventory_slots(self):
        title = self.FONT.render("Inventory", True, "white")
        self.surf.blit(title, (20, 10 + self.filled_vertical_space))
        self.filled_vertical_space += title.get_height() + 10
        index = 0
        for enemy_t, values in self.shared.values.items():
            surf = pygame.Surface((48, 48))
            surf.fill((40, 40, 40))
            if len(values) > 0:
                surf.blit(enemy_t.IMAGE, (0, 0))
                font_surf = self.FONT.render(str(len(values)), True, "yellow")
                render_at(surf, font_surf, "bottomright")

            x = (surf.get_width() + InventoryWidget.ITEM_SPACING) * index
            x += InventoryWidget.ITEM_SPACING
            y = self.filled_vertical_space
            y += InventoryWidget.ITEM_SPACING
            self.surf.blit(surf, (x, y))

            index += 1
        self.filled_vertical_space += (
            InventoryWidget.ITEM_SPACING + surf.get_height() + 20
        )

    def gen_mineral_slots(self):
        title = self.FONT.render("Minerals", True, "white")
        self.surf.blit(title, (20, 10 + self.filled_vertical_space))
        self.filled_vertical_space += title.get_height() + 10

        for index in range(2):
            surf = pygame.Surface((48, 48))
            surf.fill((40, 40, 40))

            surf.blit(self.IMAGES[index], (0, 0))
            font_surf = self.FONT.render(
                (str(self.shared.gold), str(self.shared.pyrite))[index], True, "green"
            )
            render_at(surf, font_surf, "bottomright")
            x = (surf.get_width() + InventoryWidget.ITEM_SPACING) * index
            x += InventoryWidget.ITEM_SPACING
            y = self.filled_vertical_space
            y += InventoryWidget.ITEM_SPACING
            self.surf.blit(surf, (x, y))

        self.filled_vertical_space += (
            InventoryWidget.ITEM_SPACING + surf.get_height() + 20
        )

    def gen_code_slots(self):
        self.prects: list[pygame.Rect] = []
        title = self.FONT.render("Programs", True, "white")
        self.surf.blit(title, (20, 10 + self.filled_vertical_space))
        self.filled_vertical_space += title.get_height() + 10

        for index in range(6):
            surf = pygame.Surface((48, 48))
            if index == self.chosen_index:
                color = "yellow"
            else:
                color = (40, 40, 40)
            surf.fill(color)

            if index < len(self.shared.collected_programs):
                if index == self.chosen_index:
                    self.shared.current_program = self.shared.collected_programs[index]
                    if self.shared.prg_widget is not None:
                        self.shared.prg_widget.gen_elements()
                surf.blit(self.shared.collected_programs[0].IMAGE, (0, 0))
            x = (surf.get_width() + InventoryWidget.ITEM_SPACING) * index
            x += InventoryWidget.ITEM_SPACING
            y = self.filled_vertical_space
            y += InventoryWidget.ITEM_SPACING
            self.prects.append(surf.get_rect(topleft=(x, y)))
            self.surf.blit(surf, (x, y))

    def update(self):
        self.conv_btn.update()
        clicked = False
        for event in self.shared.events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = True
        for index, rect in enumerate(self.prects):
            hover = rect.collidepoint(self.shared.cursor.pos)
            if clicked and hover:
                self.chosen_index = index
                self.shared.widgets.remove_type(ProgramWidget)
                self.shared.widgets.preview_options[pygame.K_p] = [
                    ProgramWidget,
                    "closed",
                ]
                self.shared.widgets.preview_widgets(pygame.K_p)
                self.construct()

    def draw(self):
        self.shared.screen.blit(self.surf, self.pos)
        self.conv_btn.draw()


class MessageLogWidget:
    SIZE = 400, 400
    IDEAL_POS = Shared.SCRECT.bottomright - pygame.Vector2(SIZE)
    FONT = get_font("assets/Hack/Hack Bold Nerd Font Complete Mono.ttf", 16)
    MESSAGES = []

    def __init__(self, pos) -> None:
        self.shared = Shared()
        self.surf = pygame.Surface(MessageLogWidget.SIZE)
        self.surf.fill((60, 60, 60))
        self.surf.set_alpha(150)
        self.pos = pygame.Vector2(pos)
        self.bar = VerticalScrollBar(self.surf, self.pos, 20, 100, padding=7)

        for message in MessageLogWidget.MESSAGES:
            self.bar.add(Scrollable(self.FONT.render(message, True, "white")))

        self.last_len = len(MessageLogWidget.MESSAGES)

    def update(self):
        self.bar.update()

        if self.last_len != len(MessageLogWidget.MESSAGES):
            self.bar.add(
                Scrollable(
                    self.FONT.render(MessageLogWidget.MESSAGES[-1], True, "white")
                )
            )
        if len(MessageLogWidget.MESSAGES) > 30:
            MessageLogWidget.MESSAGES.pop(0)
            self.bar.scrollables.pop(0)

        self.last_len = len(MessageLogWidget.MESSAGES)

    def draw(self):
        self.surf.fill((60, 60, 60))
        self.bar.draw()
        self.shared.screen.blit(self.surf, self.pos)


class OptionBox:
    FONT = get_font("assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 32)
    colors = {
        str: "green",
        bytes: (200, 20, 20),
        list: "orange",
        set: "red",
        int: "blue",
        dict: "springgreen",
    }

    def __init__(self, value: Any, enemy_t: Any, width: int, arg) -> None:
        self.enemy_t = enemy_t
        self.arg = arg
        self.value = value
        self.surf = pygame.Surface((width, self.FONT.get_height()))
        self.surf.set_alpha(150)
        self.fill_color_blit(self.colors.get(type(self.value)))

        self.pos = pygame.Vector2()
        self.rect = self.surf.get_rect(topleft=self.pos)
        self.shared = Shared()

    def fill_color_blit(self, color, fcolor="white"):
        self.surf.fill(color)
        self.surf.blit(self.enemy_t.IMAGE.subsurface(pygame.Rect(0, 0, 48, 48)), (0, 0))
        self.surf.blit(self.FONT.render(str(self.value), True, fcolor), (60, 0))

    def update(self, drect):
        self.rect.topleft = drect.topleft + self.pos - (self.rect.width, 0)

        if self.rect.collidepoint(self.shared.cursor.pos):
            self.fill_color_blit("white", fcolor="black")
        else:
            self.fill_color_blit(self.colors.get(type(self.value)))
        if (
            self.rect.collidepoint(self.shared.cursor.pos)
            and self.shared.cursor.clicked
        ):
            try:
                self.shared.values[self.enemy_t].remove(self.value)
            except ValueError:
                pass
            if self.shared.selected_values.get(self.arg) is not None:
                self.shared.values[self.enemy_t].append(
                    self.shared.selected_values.get(self.arg)
                )
            self.shared.selected_values[self.arg] = self.value


class DropBox:
    PADDING = 10
    WIDTH = 100
    HEIGHT = 30
    FONT = get_font("assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 20)

    def __init__(self, arg, surf, n) -> None:
        self.arg = arg
        self.shared = Shared()
        self.base_surf = surf
        self.srect = surf.get_rect()
        self.surf = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.surf.fill((40, 40, 40))
        render_at(
            self.surf,
            self.FONT.render("Select \uea9a", True, "white"),
            "center",
        )
        self.n = n
        self.pos = pygame.Vector2(
            self.srect.width - self.surf.get_width(),
            self.n * (self.surf.get_height() + self.PADDING),
        )
        self.real_rect = self.surf.get_rect(topleft=self.pos)
        self.options_surf = pygame.Surface((300, 200))
        self.options_pos = self.srect.topleft
        # self.options = VerticalScrollBar(
        #     self.options_surf, self.options_pos, width=20, height=70, padding=10
        # )
        self.options = None

    def construct_arg(self, t):
        found = False
        for enemy_t, values in self.shared.values.items():
            for value in values:
                same = isinstance(value, t)
                if same:
                    found = True
                    self.options.add(
                        OptionBox(
                            value, enemy_t, self.options_surf.get_width(), self.arg
                        )
                    )

        if not found:
            self.options.add(
                Scrollable(self.FONT.render("No items available.", True, "white"))
            )

    def construct(self):
        for arg, t in self.shared.current_program.parameter_data.items():
            if arg == self.arg:
                self.construct_arg(t)

    def update(self, pos):
        if self.options is not None:
            self.options.pos = pygame.Vector2(self.real_rect.topleft) - (300, 0)
            self.options.update()

        clicked = False
        for event in self.shared.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True

        self.real_rect.topleft = (
            self.pos
            + pos
            + (0, InventoryWidget.SIZE[1] + (self.real_rect.height // 2) + 2)
        )
        if self.real_rect.collidepoint(self.shared.cursor.pos) and clicked:
            if self.options is None:
                self.options = VerticalScrollBar(
                    self.options_surf,
                    self.real_rect.topleft,
                    width=20,
                    height=70,
                    padding=10,
                )
                self.construct()
            else:
                self.options = None

        if self.options is not None:
            for option in self.options.scrollables:
                if hasattr(option, "update"):
                    option.update(self.real_rect)

    def draw(self):
        # (self.shared.screen, "red", self.real_rect, width=3)
        self.base_surf.blit(self.surf, self.pos)
        self.options_surf.fill((40, 40, 40))
        if self.options is not None:
            self.options.draw()
            self.base_surf.blit(self.options_surf, self.pos - (300, 0))
            # for option in self.options.scrollables:
            #     if hasattr(option, "update"):
            #         pygame.draw.rect(self.shared.screen, "red", option.rect, width=3)


class ArgumentsWidget:
    FONT = get_font("assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 20)

    def __init__(self) -> None:
        self.surf = pygame.Surface((ProgramWidget.SIZE[0] - 200, 200))
        self.surf.fill((60, 60, 60))
        self.shared = Shared()
        self.pos = pygame.Vector2()
        self.arg_box: dict[str, DropBox] = {
            arg: DropBox(arg, self.surf, n)
            for n, arg in enumerate(self.shared.current_program.parameter_data)
        }
        self.shared.selected_values = {
            arg: None for arg in self.shared.current_program.parameter_data
        }

    def update(self):
        for box in self.arg_box.values():
            box.update(self.pos)

    def draw(self):
        self.surf.fill((60, 60, 60))

        index = 0
        for arg, box in self.arg_box.items():
            if self.shared.selected_values.get(arg) is not None:
                extra = self.shared.selected_values.get(arg)
            else:
                extra = "Not selected"
            surf = self.FONT.render(f"{arg}={extra}", True, "orange")
            self.surf.blit(surf, (10, index * DropBox.HEIGHT))

            box.draw()
            index += 1


class ExecuteButton:
    SIZE = 120, 40
    FONT = get_font("assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 25)

    def __init__(self) -> None:
        self.surf = pygame.Surface(self.SIZE)
        self.create_with_color("red")
        self.pos = pygame.Vector2()
        self.rect = self.surf.get_rect()
        self.shared = Shared()
        self.hover = False
        self.execute = False

    def create_with_color(self, color):
        self.surf.fill(color)
        render_at(self.surf, self.FONT.render("Execute", True, "white"), "center")

    def gen_gold(self):
        self.shared.current_program.func(**self.shared.selected_values)
        gold_gained = random.randrange(1, 8)
        self.shared.gold += gold_gained
        self.shared.messages.append(f"Gained {gold_gained} gold")

    def gen_pyrite(self):
        gained = random.randrange(3, 15)
        self.shared.pyrite += gained
        self.shared.messages.append(f"Gained {gained} pyrite")

    def on_execution(self):
        try:
            self.gen_gold()
        except Exception as e:
            self.gen_pyrite()

        self.shared.collected_programs.remove(self.shared.current_program)
        self.shared.current_program = None

        self.shared.widgets.preview_options[pygame.K_p] = [ProgramWidget, "closed"]
        self.shared.widgets.construct_widgets()

    def update(self):
        self.rect = self.surf.get_rect(
            topleft=(30, InventoryWidget.SIZE[1] + 20 + self.pos[1])
        )
        self.hover = self.rect.collidepoint(self.shared.cursor.pos)
        if self.hover:
            self.create_with_color((255, 100, 100))
        else:
            self.create_with_color("red")

        if self.hover and self.shared.cursor.clicked:
            self.execute = True
            self.on_execution()


class ProgramWidget:
    SIZE = InventoryWidget.SIZE[0], Shared.SCREEN_HEIGHT - InventoryWidget.SIZE[1] - 20
    IDEAL_POS = Shared.SCRECT.bottomleft - pygame.Vector2(0, SIZE[1])
    FONT = get_font("assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 25)
    CODE_FONT = get_font("assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 16)

    def __init__(self, pos) -> None:
        self.surf = pygame.Surface(ProgramWidget.SIZE)
        self.surf.set_alpha(150)
        self.pos = pos
        self.shared = Shared()
        self.gen_elements()

    def gen_elements(self):
        self.surf.fill((60, 60, 60))
        self.scroll_bar = VerticalScrollBar(self.surf, self.pos, 30, 100, 10)
        self.arg_widget = None
        self.exc_btn = None
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
        self.scroll_bar.add(Scrollable(self.FONT.render("Code", True, "white")))
        self.scroll_bar.add(
            Scrollable(
                self.CODE_FONT.render(
                    self.shared.current_program.code_text, True, "green"
                )
            )
        )

    def gen_arguments_element(self):
        self.scroll_bar.add(
            Scrollable(self.FONT.render("\n\nArguments", True, "white"))
        )
        self.arg_widget = ArgumentsWidget()
        self.scroll_bar.add(self.arg_widget)

    def gen_execute_element(self):
        self.exc_btn = ExecuteButton()
        self.scroll_bar.add(self.exc_btn)

    def update(self):
        if self.arg_widget is not None:
            self.arg_widget.update()

        if self.exc_btn is not None:
            self.exc_btn.update()

        self.scroll_bar.update()

    def draw(self):
        self.surf.fill((60, 60, 60))
        if self.arg_widget is not None:
            self.arg_widget.draw()
        self.scroll_bar.draw()
        self.shared.screen.blit(self.surf, self.pos)


class MiniMapWidget:
    SIZE = 400, 400
    IDEAL_POS = Shared.SCRECT.topright - pygame.Vector2(SIZE[0], 0)

    def __init__(self, pos) -> None:
        self.shared = Shared()
        self.surf = pygame.Surface(MessageLogWidget.SIZE)
        self.surf.fill((60, 60, 60))
        self.surf.set_alpha(150)
        self.pos = pygame.Vector2(pos)
        self.cam = Camera()

    def render_platform(self, platform):
        if platform in self.shared.current_chunks:
            color = "green"
        else:
            color = self.shared.cursor.surface_color
        surf = pygame.Surface((8, 8))
        surf.fill(color)
        for row in platform.blocks:
            for block in row:
                pos = (
                    block.iso_pos[0] * surf.get_width(),
                    block.iso_pos[1] * surf.get_height(),
                )
                self.surf.blit(surf, self.cam.transform_mini(pos))

    def update(self):
        try:
            self.cam.attach_to_mini(self.SIZE)
        except:
            pass

    def draw(self):
        self.surf.fill((60, 60, 60))
        for platform in self.shared.plat.platforms:
            self.render_platform(platform)

        self.shared.screen.blit(self.surf, self.pos)


class ConvertButton:
    FONT = get_font("assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 16)

    def __init__(self) -> None:
        self.surf = pygame.Surface((100, 20))
        self.surf.fill("red")
        self.pos = (150, 180)
        self.rect = self.surf.get_rect(topleft=self.pos)
        self.shared = Shared()
        self.font_surf = self.FONT.render("Convert", True, "white")
        self.font_rect = self.font_surf.get_rect(center=self.rect.center)

    def update(self):
        if self.rect.collidepoint(self.shared.cursor.pos):
            hover = True
            self.surf.fill("orange")
        else:
            hover = False
            self.surf.fill("red")

        if hover and self.shared.cursor.clicked and self.shared.pyrite >= 3:
            self.shared.gold += 1
            self.shared.pyrite -= 3
            self.shared.messages.append("Traded 3 pyrite for 1 gold")
            self.shared.inv_widget.construct()

    def draw(self):
        self.shared.screen.blit(self.surf, self.rect)
        self.shared.screen.blit(self.font_surf, self.font_rect)
