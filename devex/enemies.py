import pygame
import random
from .utils import (
    load_scale_3,
    iso_to_screen,
    get_font,
    SinWave,
    PlayItOnceAnimation,
)
from abc import ABC
from .shared import Shared
import itertools
import string


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
        health: int = 100,
        bouncy_direction: str = "vertical",
    ) -> None:
        self.shared = Shared()
        self.data_type = data_type
        self.data_font_color = data_font_color
        self.original_image = image.copy()
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.broken_platform_size = broken_platform_size
        self.origin = origin
        self.bouncy_direction = bouncy_direction
        self.health = health
        self.alive = True

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

        """Image morphing"""
        if bouncy_direction == "vertical":
            self.size = self.image.get_height()
        else:
            self.size = self.image.get_width()
        self.original_size = self.size
        self.bouncy_wave = SinWave(0.06)
        self.taking_damage = False
        self.higlight_alpha = 200

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

    def highlight_red(self):
        if not self.taking_damage:
            return

        surf = pygame.Surface(self.image.get_size())
        surf.fill("red")
        surf.set_alpha(self.higlight_alpha)
        self.higlight_alpha -= 100 * self.shared.dt
        if self.higlight_alpha <= 120:
            self.taking_damage = False
            self.higlight_alpha = 200
        self.image.blit(surf, (0, 0))

    def take_damage(self):
        for fireball in self.shared.player.fireball_manager.fireballs:
            if fireball.rect.colliderect(self.rect):
                fireball.alive = False
                self.shared.play_it_once_anims.append(
                    PlayItOnceAnimation(
                        fireball.EXPLOSION_FRAMES, 0.08, self.pos - (64, 64)
                    )
                )
                self.health -= fireball.damage
                self.taking_damage = True

        if self.health <= 0:
            self.alive = False
            self.shared.slots[type(self)] += 1

    def set_font_surf(self):
        self.font_surf = self.font.render(str(self.value), True, self.data_font_color)
        self.font_rect = self.font_surf.get_rect()

    def move(self):
        self.pos.move_towards_ip(self.current_target, self.speed * self.shared.dt)
        if self.pos == self.current_target:
            self.current_target = next(self.targets)

        self.rect.midbottom = self.pos
        self.font_rect.midtop = self.pos

    def morph_image(self):
        """Create a bouncy animation for the enemy"""

        self.size = self.original_size + (self.bouncy_wave.val() * 5)
        if self.bouncy_direction == "vertical":
            new_size = self.original_image.get_width(), self.size
        else:
            new_size = self.size, self.original_image.get_height()
        self.image = pygame.transform.scale(self.original_image, new_size)

    def update(self):
        self.move()
        self.morph_image()
        self.take_damage()
        self.highlight_red()

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

        self.value = random.choice(
            (random.randrange(100, 10000), random.randrange(1, 10))
        )
        self.set_font_surf()


class CentiSet(Enemy):
    IMAGE = load_scale_3("assets/set.png")
    SPEED = 25

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
            CentiSet.IMAGE,
            iso_pos,
            broken_platform_size,
            tile_rect,
            CentiSet.SPEED,
            origin,
            bouncy_direction="horizontal",
        )

        self.value = {random.randrange(1, 10) for _ in range(random.randrange(2, 5))}
        self.set_font_surf()


class BeeList(Enemy):
    IMAGE = load_scale_3("assets/list.png")
    SPEED = 15

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
            BeeList.IMAGE,
            iso_pos,
            broken_platform_size,
            tile_rect,
            BeeList.SPEED,
            origin,
        )

        self.value = [random.randrange(1, 10) for _ in range(random.randrange(2, 5))]
        self.set_font_surf()


class HumanStr(Enemy):
    IMAGE = load_scale_3("assets/str.png")
    SPEED = 35

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
            HumanStr.IMAGE,
            iso_pos,
            broken_platform_size,
            tile_rect,
            HumanStr.SPEED,
            origin,
        )

        list_str = list(string.ascii_lowercase[: random.randrange(4, 8)])
        random.shuffle(list_str)
        list_str = "".join(list_str)
        self.value = f'"{list_str}"'
        self.set_font_surf()


class PoopyBytes(Enemy):
    IMAGE = load_scale_3("assets/bytes.png")
    SPEED = 45

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
            PoopyBytes.IMAGE,
            iso_pos,
            broken_platform_size,
            tile_rect,
            PoopyBytes.SPEED,
            origin,
        )

        list_str = list(string.ascii_lowercase[: random.randrange(4, 8)])
        random.shuffle(list_str)
        list_str = "".join(list_str)
        self.value = f'b"{list_str}"'
        self.set_font_surf()
