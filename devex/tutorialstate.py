from pathlib import Path

import pygame

from .shared import Shared
from .state_enums import State
from .utils import get_font, render_at
from .widgets import Widgets


def load_page(path: str):
    """
    new_width = min(width / SCREEN_WIDTH, height / SCREEN_HEIGHT) * SCREEN_WIDTH
    new_height = min(width / SCREEN_WIDTH, height / SCREEN_HEIGHT) * SCREEN_HEIGHT
    """

    image = pygame.image.load(path).convert()
    width, height = image.get_size()
    SCREEN_WIDTH, SCREEN_HEIGHT = Shared.SCRECT.size

    new_width = min(width / SCREEN_WIDTH, height / SCREEN_HEIGHT) * SCREEN_WIDTH
    new_height = min(width / SCREEN_WIDTH, height / SCREEN_HEIGHT) * SCREEN_HEIGHT

    return pygame.transform.scale(image, (new_width, new_height))


class PreviewTutorial:
    def __init__(self) -> None:
        self.font = get_font("assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 32)
        self.big_font = get_font(
            "assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 64
        )
        self.shared = Shared()
        self.overlay = pygame.Surface(Shared.SCRECT.size)

        self.load_tutorial()
        self.pic_index = 0
        self.current_pic = self.pics[self.pic_index]
        self.info_surf = self.font.render(
            """
D, RIGHT - Next page
A, LEFT - Previous page
ENTER - Main Menu
            """,
            True,
            "white",
            "black",
        )
        self.info_surf.set_alpha(150)
        self.page_surf = self.font.render(
            f"Page {self.pic_index + 1}/{len(self.pics)}", True, "white", "black"
        )

    def load_tutorial(self):
        n_files = len(tuple(Path("assets/tutorial/").iterdir()))
        self.pics: list[pygame.Surface] = [
            load_page(f"assets/tutorial/{i}.png") for i in range(1, n_files + 1)
        ]

    def update(self):
        for event in self.shared.events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.pic_index += 1
                    if self.pic_index >= len(self.pics):
                        self.pic_index = 0
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.pic_index -= 1
                    if self.pic_index <= -1:
                        self.pic_index = len(self.pics) - 1

                if event.key not in (
                    pygame.K_RIGHT,
                    pygame.K_d,
                    pygame.K_LEFT,
                    pygame.K_a,
                ):
                    continue
                self.page_surf = self.font.render(
                    f"Page {self.pic_index + 1}/{len(self.pics)}",
                    True,
                    "white",
                    "black",
                )
        self.current_pic = self.pics[self.pic_index]

    def draw(self):
        render_at(self.shared.screen, self.current_pic, "center")
        render_at(self.shared.screen, self.page_surf, "midtop")
        render_at(self.shared.screen, self.info_surf, "topright")


class TutorialState:
    REQUIRED_FIELDS = ["screen"]

    def __init__(self) -> None:
        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.next_state = None
        self.shared = Shared()
        self.clean_shared_data()
        self.shared.widgets = Widgets(style="gameover")
        self.preview = PreviewTutorial()

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
