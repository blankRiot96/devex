import pygame
import typing as t
from functools import lru_cache
import time
import itertools
import math


class SinWave:
    def __init__(self, speed: float) -> None:
        self.rad = 0.0
        self.speed = speed

    def val(self) -> float:
        self.rad += self.speed
        if self.rad >= 2 * math.pi:
            self.rad = 0

        return math.sin(self.rad)


class Time:
    """
    Class to check if time has passed.
    """

    def __init__(self, time_to_pass: float):
        self.time_to_pass = time_to_pass
        self.start = time.perf_counter()

    def tick(self) -> bool:
        if time.perf_counter() - self.start > self.time_to_pass:
            self.start = time.perf_counter()
            return True
        return False


class Animation:
    def __init__(
        self, frames: t.Sequence[pygame.Surface], time_between_frames: float
    ) -> None:
        self.frames = itertools.cycle(frames)
        self.timer = Time(time_between_frames)
        self.current_frame = next(self.frames)

    def update(self):
        if self.timer.tick():
            self.current_frame = next(self.frames)


@lru_cache
def get_font(file_name: str | None, size: t.Sequence) -> pygame.font.Font:
    return pygame.font.Font(file_name, size)


def circle_surf(radius: float, color) -> pygame.Surface:
    surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(surf, color, (radius, radius), radius)
    return surf


def render_at(
    base_surf: pygame.Surface,
    surf: pygame.Surface,
    pos: str,
    offset: t.Sequence = (0, 0),
) -> None:
    """Renders a surface to a base surface by matching a point.

    Example: render_at(screen, widget, "center")
    """
    base_rect = base_surf.get_rect()
    surf_rect = surf.get_rect()
    setattr(surf_rect, pos, getattr(base_rect, pos))
    surf_rect.x += offset[0]
    surf_rect.y += offset[1]
    base_surf.blit(surf, surf_rect)


def iso_to_screen(iso_pos: t.Sequence, tile_rect: pygame.Rect) -> t.Sequence:
    """Converts isometric position to screen space"""

    x, y = iso_pos
    screen_x = (x - y) * (tile_rect.width / 2)
    screen_y = (x + y) * (tile_rect.height / 4)

    return screen_x, screen_y


def load_scale_3(file_path: str) -> pygame.Surface:
    img = pygame.image.load(file_path).convert_alpha()
    return pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))


def scale_by(img: pygame.Surface, factor: float | int) -> pygame.Surface:
    return pygame.transform.scale(
        img, (img.get_width() * factor, img.get_height() * factor)
    )


def scale_add(img: pygame.Surface, term: float | int) -> pygame.Surface:
    return pygame.transform.scale(
        img, (img.get_width() + term, img.get_height() + term)
    )
