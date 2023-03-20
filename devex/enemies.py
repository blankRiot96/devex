import pygame
import random
from .utils import load_scale_3, iso_to_screen, get_font
from abc import ABC
from .shared import Shared
import itertools


class Enemy(ABC):
    font = get_font("assets/Hack/Hack Bold Nerd Font Complete.ttf", 16)

    def __init__(
        self,
        data_type: type,
        data_font_color,
        image: pygame.Surface,
        iso_pos: tuple[int, int],
        broken_platform_size: int,
        tile_rect: pygame.Rect,
        enemy_speed: float,
        origin: tuple[int, int],
    ) -> None:
        self.shared = Shared()
        self.data_type = data_type
        self.data_font_color = data_font_color
        self.image = image
        self.rect = self.image.get_rect()
        self.broken_platform_size = broken_platform_size
        self.origin = origin

        """
        So, the iso_pos is basically gonna hold a value such as
        (2, 3). Here the enemy will move across a few tiles. Maybe the path is:
        (2, 3) -> (3, 3) -> (4, 3) -> (5, 3)
        """
        self.iso_pos = iso_pos
        self.iso_path_range = self.calc_path_range()
        self.initial_screen_pos = iso_to_screen(self.iso_path_range[0], tile_rect)
        self.final_screen_pos = iso_to_screen(self.iso_path_range[-1], tile_rect)

        self.targets = itertools.cycle((self.initial_screen_pos, self.final_screen_pos))
        self.current_target = self.initial_screen_pos
        self.pos = pygame.Vector2(self.initial_screen_pos)
        self.speed = enemy_speed

    def calc_path_range(self) -> None:
        """Calculates the path range for the enemy."""

        # Random parameters
        n_steps: int = random.randrange(3, self.broken_platform_size - 2)
        x_or_y: int = random.randint(0, 1)

        # Applies the parameters
        axis_range_x = range(1 + self.origin[0], n_steps + self.origin[0])
        axis_range_y = range(1 + self.origin[1], n_steps + self.origin[1])

        # Produces the result
        if x_or_y:
            return [(self.iso_pos[0], axis) for axis in axis_range_y]

        return [(axis, self.iso_pos[1]) for axis in axis_range_x]

    def set_font_surf(self):
        self.font_surf = self.font.render(str(self.value), True, self.data_font_color)
        self.font_rect = self.font_surf.get_rect()

    def update(self):
        self.pos.move_towards_ip(self.current_target, self.speed * self.shared.dt)
        if self.pos == self.current_target:
            self.current_target = next(self.targets)

        self.rect.midbottom = self.pos
        self.font_rect.midtop = self.pos

    def draw(self):
        self.shared.screen.blit(self.image, self.shared.camera.transform(self.rect))
        self.shared.screen.blit(
            self.font_surf, self.shared.camera.transform(self.font_rect)
        )


class PotatoInt(Enemy):
    IMAGE = load_scale_3("assets/integer.png")
    SPEED = 30

    def __init__(
        self, broken_platform_size: int, tile_rect: pygame.Rect, origin: tuple[int, int]
    ) -> None:
        iso_pos = (
            random.randrange(2, broken_platform_size - 2) + origin[0],
            random.randrange(2, broken_platform_size - 2) + origin[1],
        )
        super().__init__(
            int,
            "pink",
            PotatoInt.IMAGE,
            iso_pos,
            broken_platform_size,
            tile_rect,
            PotatoInt.SPEED,
            origin,
        )

        self.value = random.randrange(100, 10000)
        self.set_font_surf()
