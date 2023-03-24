import itertools
import math
from enum import Enum, auto

import pygame

from .shared import Shared
from .utils import scale_by


class CursorState(Enum):
    TOUCHABLE = auto()
    FORBIDDEN = auto()
    ATTACK = auto()
    USER_INTERFACE = auto()


class CursorAnimation:
    def __init__(self, target_pos) -> None:
        self.original_image = pygame.image.load(
            "assets/cursor-anim.png"
        ).convert_alpha()
        self.original_image = scale_by(self.original_image, 0.5)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.pos = target_pos
        self.size = self.original_image.get_width()
        self.shared = Shared()
        self.reduction_speed = 140
        self.min_size = self.size / 3
        self.alpha = 255
        self.alive = True

    def update(self):
        self.image = pygame.transform.scale(self.original_image, (self.size, self.size))
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect(center=self.pos)

        if self.size > self.min_size:
            self.size -= self.shared.dt * self.reduction_speed
        else:
            self.size = self.min_size

        if self.alpha > 0:
            self.alpha -= 200 * self.shared.dt
        else:
            self.alive = False

    def draw(self):
        self.shared.screen.blit(self.image, self.shared.camera.transform(self.rect))


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
            CursorState.USER_INTERFACE: pygame.transform.scale(
                pygame.image.load("assets/cursor-ui.png").convert_alpha(), (25, 25)
            ),
        }
        pygame.mouse.set_cursor(
            pygame.cursors.Cursor((0, 0), self.images.get(self.state))
        )
        self.surface_color = pygame.Color((50, 83, 95))
        self.player_target = None
        self.anim: CursorAnimation | None = None
        self.radians_between_player = 0.0
        self.clicked = False

    @property
    def state(self) -> CursorState:
        return self.__state

    @state.setter
    def state(self, new_state: CursorState) -> None:
        self.__state = new_state

    def collect_pos(self):
        self.pos = pygame.mouse.get_pos()
        self.trans_pos = self.pos + self.shared.camera.offset
        self.radians_between_player = math.atan2(
            self.trans_pos.y - self.shared.player.pos.y,
            self.trans_pos.x - self.shared.player.pos.x,
        )

    def on_forbidden(self):
        try:
            if (
                self.shared.provisional_chunk.get_at(self.pos) != self.surface_color
                and self.state != CursorState.USER_INTERFACE
            ):
                self.state = CursorState.FORBIDDEN
            elif self.state != CursorState.USER_INTERFACE:
                self.state = CursorState.TOUCHABLE
        except IndexError:
            pass

    def on_attack(self):
        for chunk in self.shared.current_chunks:
            for enemy in chunk.enemies:
                if enemy.rect.collidepoint(self.trans_pos):
                    self.state = CursorState.ATTACK

    def on_click(self):
        self.clicked = False
        for event in self.shared.events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.clicked = True

        for event in self.shared.events:
            mouse_clicked = event.type == pygame.MOUSEBUTTONDOWN
            is_touchable = self.state == CursorState.TOUCHABLE

            if mouse_clicked and is_touchable and event.button == 3:
                self.player_target = self.trans_pos
                self.anim = CursorAnimation(self.trans_pos)

    def set_cursor(self):
        pygame.mouse.set_cursor(
            pygame.cursors.Cursor((0, 0), self.images.get(self.state))
        )

    def on_anim(self):
        if self.anim is not None:
            self.anim.update()
            if not self.anim.alive:
                self.anim = None

    def update(self):
        self.collect_pos()
        self.on_forbidden()
        self.on_click()
        self.on_attack()
        self.set_cursor()
        self.on_anim()

    def draw(self):
        if self.anim is not None:
            self.anim.draw()
