import pygame
from .shared import Shared
from enum import Enum, auto


class CursorState(Enum):
    TOUCHABLE = auto()
    FORBIDDEN = auto()
    ATTACK = auto()


class Cursor:
    def __init__(self) -> None:
        self.shared = Shared()
        self.pos = pygame.Vector2()
        self.__state: CursorState = CursorState.TOUCHABLE
        self.images = {
            CursorState.TOUCHABLE: pygame.transform.scale(
                pygame.image.load("assets/cursor-touchable.png").convert_alpha(),
                (25, 25),
            ),
            CursorState.ATTACK: pygame.transform.scale(
                pygame.image.load("assets/cursor-attack.png").convert_alpha(), (25, 25)
            ),
            CursorState.FORBIDDEN: pygame.image.load(
                "assets/cursor-forbidden.png"
            ).convert_alpha(),
        }
        pygame.mouse.set_cursor(
            pygame.cursors.Cursor((0, 0), self.images.get(self.state))
        )
        self.surface_color = pygame.Color((50, 83, 95))
        self.player_target = None

    @property
    def state(self) -> CursorState:
        return self.__state

    @state.setter
    def state(self, new_state: CursorState) -> None:
        self.__state = new_state
        pygame.mouse.set_cursor(
            pygame.cursors.Cursor((0, 0), self.images.get(new_state))
        )

    def collect_pos(self):
        self.pos = pygame.mouse.get_pos()

    def on_forbidden(self):
        try:
            if self.shared.provisional_chunk.get_at(self.pos) != self.surface_color:
                self.state = CursorState.FORBIDDEN
            else:
                self.state = CursorState.TOUCHABLE
        except IndexError:
            pass

    def on_click(self):
        for event in self.shared.events:
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and self.state == CursorState.TOUCHABLE
            ):
                self.player_target = event.pos + self.shared.camera.offset

    def update(self):
        self.collect_pos()
        self.on_forbidden()
        self.on_click()
