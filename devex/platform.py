import random
import pygame
from .utils import iso_to_screen, get_font
from .shared import Shared


class Block:
    img = pygame.image.load("assets/brick_block_1.png").convert_alpha()

    def __init__(self, iso_pos) -> None:
        self.iso_pos = iso_pos
        self.rect = self.img.get_rect()
        self.screen_pos = iso_to_screen((iso_pos[0] + 10, iso_pos[1] + 1), self.rect)
        self.shared = Shared()

    def update(self):
        ...

    def draw(self):
        self.shared.game_screen.blit(self.img, self.screen_pos)


class BrokenPlatform:
    """A platform with a random spec"""

    def __init__(self) -> None:
        self.side = random.randrange(8, 13)
        self.generate_base()
        self.chip_extra_sides()

    def generate_base(self):
        self.blocks = []
        for y in range(self.side):
            row = []
            for x in range(self.side):
                row.append(Block((x, y)))
            self.blocks.append(row)

    def chip_extra_sides(self):
        for y, row in tuple(enumerate(self.blocks)):
            for x, block in tuple(enumerate(row)):
                if random.random() > 0.5:
                    continue
                if 0 in (x, y) or (self.side - 1) in (x, y):
                    self.blocks[y].remove(block)

    def update(self):
        for row in self.blocks:
            for block in row:
                block.update()

    def draw(self):
        for row in self.blocks:
            for block in row:
                block.draw()
