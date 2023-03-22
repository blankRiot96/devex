import random
import pygame
from enum import Enum, auto
from .utils import get_font, iso_to_screen, load_scale_3, Time, Animation
from .bloom import Bloom
from .shared import Shared
from .enemies import Enemy, PotatoInt, HumanStr, PoopyBytes, BeeList, CentiSet
from logit import log


class Block:
    img = load_scale_3("assets/brick_block_1.png")

    def __init__(self, iso_pos) -> None:
        self.iso_pos = iso_pos
        self.shared = Shared()
        self.rect = self.img.get_rect()
        self.screen_pos = iso_to_screen(iso_pos, self.rect)
        self.pos = pygame.Vector2(self.screen_pos[0], self.screen_pos[1] + 150)
        self.start_timer = Time(random.uniform(0, 3))
        self.done = False
        self.done_waiting = False
        self.speed = 500

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
        if not self.done_waiting:
            return
        self.shared.screen.blit(self.img, self.shared.camera.transform(self.pos))


class TorchSide(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class Torch:
    FRAMES = tuple(load_scale_3(f"assets/torch-{i}.png") for i in range(1, 4))
    FONT = get_font("assets/Hack/Hack Regular Nerd Font Complete Mono.ttf", 16)
    BRIDGE_GAP = 5

    def __init__(self, origin: tuple[int, int], side: TorchSide, world_side) -> None:
        self.side = world_side
        self.origin = origin
        self.path_side = side
        self.gen_iso_coord()
        self.anim = Animation(Torch.FRAMES, 0.3)
        self.bloom = Bloom(0.6, wave_speed=0.01, expansion_factor=20)
        self.shared = Shared()
        self.screen_coord = iso_to_screen(
            self.iso_coord, pygame.Rect(0, 0, 32 * 3, 32 * 3)
        )
        self.rect = self.anim.current_frame.get_rect(midbottom=self.screen_coord)
        self.create_surf = Torch.FONT.render("[+] CREATE", True, "purple", "white")
        self.create_surf_rect = self.create_surf.get_rect(midbottom=self.rect.midtop)
        self.near = False
        self.used = False

    def get_inverse_side(self):
        if self.path_side == TorchSide.UP:
            return TorchSide.DOWN
        if self.path_side == TorchSide.DOWN:
            return TorchSide.UP
        if self.path_side == TorchSide.RIGHT:
            return TorchSide.LEFT
        if self.path_side == TorchSide.LEFT:
            return TorchSide.RIGHT

    def gen_iso_coord(self):
        if self.path_side == TorchSide.UP:
            self.iso_coord = (self.side // 2), 1
            self.add_origin()
            self.new_plat_iso_coord = (
                self.iso_coord[0],
                self.iso_coord[1] - Torch.BRIDGE_GAP - self.side,
            )
        elif self.path_side == TorchSide.LEFT:
            self.iso_coord = 2, (self.side // 2)
            self.add_origin()
            self.new_plat_iso_coord = (
                self.iso_coord[0] - Torch.BRIDGE_GAP - self.side,
                self.iso_coord[1],
            )
        elif self.path_side == TorchSide.DOWN:
            self.iso_coord = (
                (self.side // 2),
                self.side - 2,
            )
            self.add_origin()
            self.new_plat_iso_coord = (
                self.iso_coord[0],
                self.iso_coord[1] + Torch.BRIDGE_GAP,
            )
        elif self.path_side == TorchSide.RIGHT:
            self.iso_coord = (
                self.side - 1,
                (self.side // 2),
            )
            self.add_origin()
            self.new_plat_iso_coord = (
                self.iso_coord[0] + Torch.BRIDGE_GAP,
                self.iso_coord[1],
            )

    def add_origin(self):
        self.iso_coord = (
            self.iso_coord[0] + self.origin[0],
            self.iso_coord[1] + self.origin[1],
        )

    def check_near(self):
        self.near = self.shared.player.rect.colliderect(self.rect)

    def on_create_chunk(self):
        for event in self.shared.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_EQUALS and self.near:
                    self.used = True

    def update(self):
        self.anim.update()
        self.bloom.update(self.shared.camera.transform(self.rect.center))

        self.check_near()
        self.on_create_chunk()

    def draw(self):
        self.shared.screen.blit(
            self.anim.current_frame, self.shared.camera.transform(self.rect)
        )
        self.bloom.draw(self.shared.overlay)

        if self.near:
            self.shared.screen.blit(
                self.create_surf, self.shared.camera.transform(self.create_surf_rect)
            )


class BrokenPlatform:
    """A platform with a random spec"""

    def __init__(self, side: int, origin: tuple[int, int]) -> None:
        self.origin = origin
        self.side = side
        self.shared = Shared()
        self.generate_base()
        self.chip_extra_sides()
        self.get_rect()
        self.generate_enemies()
        self.generate_torches()
        self.done = False

    def generate_torches(self) -> None:
        self.torches: list[Torch] = [
            Torch(self.origin, side, self.side) for side in TorchSide
        ]

    def generate_enemies(self):
        n_enemies = int(self.side / 2.5)
        self.enemies: list[Enemy] = []
        for _ in range(n_enemies):
            enemy_type = random.choice(
                (PotatoInt, HumanStr, PoopyBytes, BeeList, CentiSet)
            )
            self.enemies.append(
                enemy_type(self.side, self.blocks[1][1].rect, self.origin)
            )

    def generate_base(self):
        self.blocks = []
        for y in range(self.side):
            row = []
            for x in range(self.side):
                row.append(Block((x + self.origin[0], y + self.origin[1])))
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
        for enemy in self.enemies[:]:
            enemy.update()

            if not enemy.alive:
                self.enemies.remove(enemy)

    def update_torches(self):
        for torch in self.torches:
            torch.update()

    def update(self):
        self.update_blocks()
        if self.done:
            self.update_torches()
            self.update_enemies()
        self.done = self.get_done()

    def get_rect(self):
        self.rect = pygame.Rect(
            self.blocks[-1][0].pos,
            (
                self.side * self.blocks[0][0].rect.width,
                self.side * self.blocks[0][0].rect.height,
            ),
        )
        self.rect.center = self.blocks[0][0].pos

    def draw_blocks(self):
        for row in self.blocks:
            for block in row:
                block.draw()

    def draw_enemies(self):
        for enemy in self.enemies:
            enemy.draw()

    def draw_torches(self):
        for torch in self.torches:
            torch.draw()


class PlatformManager:
    def __init__(self) -> None:
        self.shared = Shared()
        self.platforms: list[BrokenPlatform] = [
            BrokenPlatform(side=random.randrange(8, 13), origin=(0, 0))
        ]
        self.shared.current_chunk = self.platforms[0]
        self.done = False

    def update_platforms(self):
        for platform in self.platforms:
            platform.update()
            if platform.rect.colliderect(self.shared.player.rect):
                self.shared.current_chunk = platform

        self.done = all(platform.done for platform in self.platforms)

    def create_new_plat(self, torch: Torch, platform: BrokenPlatform):
        side = random.randrange(7, 10)
        new_plat = BrokenPlatform(
            side,
            origin=torch.new_plat_iso_coord,
        )
        for new_torch in new_plat.torches:
            if new_torch.path_side == torch.get_inverse_side():
                new_plat.torches.remove(new_torch)
                break
        self.platforms.append(new_plat)
        platform.torches.clear()

    def update_torches(self):
        for platform in self.platforms[:]:
            for torch in platform.torches:
                if torch.used:
                    self.create_new_plat(torch, platform)
                    return

    def update(self):
        self.update_platforms()
        self.update_torches()

    def draw_torches(self):
        for platform in self.platforms:
            platform.draw_torches()

    def draw(self):
        for platform in self.platforms:
            platform.draw_blocks()
        self.shared.provisional_chunk = self.shared.screen.copy()

        for platform in self.platforms:
            if platform.done:
                platform.draw_enemies()
