import pygame
import typing as t
from functools import lru_cache


@lru_cache
def get_font(file_name: str | None, size: t.Sequence) -> pygame.font.Font:
    return pygame.font.Font(file_name, size)


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
