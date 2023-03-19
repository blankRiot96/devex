import random
import pygame
from .utils import iso_to_screen, load_scale_3, Time
from .shared import Shared
from .enemies import PotatoInt, Enemy


class Block:
    img = load_scale_3("assets/brick_block_1.png")

    def __init__(self, iso_pos) -> None:
        self.iso_pos = iso_pos[0] + 10, iso_pos[1] + 1
        self.shared = Shared()
        self.rect = self.img.get_rect()
        self.screen_pos = iso_to_screen(iso_pos, self.rect)
        self.pos = pygame.Vector2(self.screen_pos[0], self.shared.SCREEN_HEIGHT)
        self.start_timer = Time(random.uniform(0, 5))
        self.done = False
        self.done_waiting = False
        self.speed = 300

    def update(self):
        if not self.done_waiting and not self.start_timer.tick():
            return
        self.done_waiting = True

        if self.pos == self.screen_pos:
            self.done = True
            return

        self.pos.move_towards_ip(self.screen_pos, self.speed * self.shared.dt)
        self.speed += 500 * self.shared.dt

    def draw(self):
        self.shared.screen.blit(self.img, self.shared.camera.transform(self.pos))


class BrokenPlatform:
    """A platform with a random spec"""

    def __init__(self) -> None:
        self.side = random.randrange(8, 13)
        self.generate_base()
        self.chip_extra_sides()
        self.generate_enemies()
        self.done = False

    def generate_enemies(self):
        n_enemies = int(self.side / 2.5)
        self.enemies = []
        for _ in range(n_enemies):
            enemy_type = PotatoInt
            # enemy_type = random.choice((PotatoInt, ...))
            self.enemies.append(PotatoInt(self.side, self.blocks[0][0].rect))

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

    def get_done(self) -> bool:
        for row in self.blocks:
            for block in row:
                if not block.done:
                    return False
        return True

    def update_blocks(self):
        for row in self.blocks:
            for block in row:
                block.update()

    def update_enemies(self):
        for enemy in self.enemies:
            enemy.update()

    def update(self):
        self.update_blocks()
        if self.done:
            self.update_enemies()
        self.done = self.get_done()

    def draw_blocks(self):
        for row in self.blocks:
            for block in row:
                block.draw()

    def draw_enemies(self):
        for enemy in self.enemies:
            enemy.draw()

    def draw(self):
        self.draw_blocks()
        if self.done:
            self.draw_enemies()


class PlatformManager:
    def __init__(self) -> None:
        self.platforms: list[BrokenPlatform] = [BrokenPlatform()]
        self.shared = Shared()
        self.done = False

    def update_platforms(self):
        for platform in self.platforms:
            platform.update()
        self.done = all(platform.done for platform in self.platforms)

    def update(self):
        self.update_platforms()

    def draw(self):
        for platform in self.platforms:
            platform.draw()
        self.shared.provisional_chunk = self.shared.screen.copy()
