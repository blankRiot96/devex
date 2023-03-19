import pygame
from .utils import scale_by, scale_add, SinWave


def process_bloom(img: pygame.Surface) -> pygame.Surface:
    raw = pygame.Surface(img.get_size())
    raw.blit(img, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    raw.blit(img, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    return raw


class Bloom:
    IMAGE = pygame.image.load("assets/light.png").convert()
    # IMAGE = process_bloom(IMAGE)

    def __init__(self, size_factor: float | int) -> None:
        self.size_factor = size_factor
        self.original_surf = scale_by(self.IMAGE, size_factor)
        self.surf = self.original_surf.copy()
        self.rect = self.surf.get_rect()
        self.wave = SinWave(0.02)

    def update(self, pos):
        self.surf = scale_add(self.original_surf, self.wave.val() * 70)
        self.rect = self.surf.get_rect()
        self.rect.center = pos

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surf, self.rect)
