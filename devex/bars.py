import pygame

from .shared import Shared
from .utils import render_at, scale_by


class HealthBar:
    LOGO = pygame.image.load("assets/heart.png").convert_alpha()
    LOGO = scale_by(LOGO, 0.05)
    BAR_SIZE = 500, 15

    def __init__(self) -> None:
        self.shared = Shared()
        self.background_surf = pygame.Surface(self.BAR_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(
            self.background_surf,
            (255, 200, 200),
            pygame.Rect(0, 0, *self.BAR_SIZE),
            border_radius=7,
        )
        self.original_foreground_surf = pygame.Surface(self.BAR_SIZE)
        self.original_foreground_surf.fill("red")
        self.foreground_surf = self.original_foreground_surf.copy()
        self.size = self.BAR_SIZE

    def update(self):
        self.size = (
            self.shared.player.health / self.shared.player.MAX_HEALTH
        ) * self.BAR_SIZE[0], self.BAR_SIZE[1]

        self.foreground_surf = pygame.Surface(self.BAR_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(
            self.foreground_surf,
            "red",
            pygame.Rect(0, 0, *self.size),
            border_radius=7,
        )

    def draw(self):
        render_at(self.shared.screen, self.background_surf, "midtop", (0, 20))
        render_at(self.shared.screen, self.foreground_surf, "midtop", (0, 20))

        render_at(
            self.shared.screen,
            self.LOGO,
            "midtop",
            (-self.LOGO.get_width() + 20 - (self.BAR_SIZE[0] / 2), 15),
        )


class EnergyBar:
    LOGO = pygame.image.load("assets/energy.png").convert_alpha()
    LOGO = scale_by(LOGO, 1.5)
    BAR_SIZE = 500, 15

    def __init__(self) -> None:
        self.shared = Shared()
        self.background_surf = pygame.Surface(self.BAR_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(
            self.background_surf,
            (40, 40, 180),
            pygame.Rect(0, 0, *self.BAR_SIZE),
            border_radius=7,
        )
        self.original_foreground_surf = pygame.Surface(self.BAR_SIZE)
        self.original_foreground_surf.fill("cyan")
        self.foreground_surf = self.original_foreground_surf.copy()
        self.size = self.BAR_SIZE

    def update(self):
        self.size = (
            self.shared.player.mana / self.shared.player.MAX_ENERGY
        ) * self.BAR_SIZE[0], self.BAR_SIZE[1]

        self.foreground_surf = pygame.Surface(self.BAR_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(
            self.foreground_surf,
            "cyan",
            pygame.Rect(0, 0, *self.size),
            border_radius=7,
        )

    def draw(self):
        render_at(self.shared.screen, self.background_surf, "midtop", (0, 50))
        render_at(self.shared.screen, self.foreground_surf, "midtop", (0, 50))

        render_at(
            self.shared.screen,
            self.LOGO,
            "midtop",
            (-self.LOGO.get_width() + 20 - (self.BAR_SIZE[0] / 2), 45),
        )
