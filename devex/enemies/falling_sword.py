import pygame

from devex.shared import Shared
from devex.utils import SinWave, Time, load_scale_3, scale_by


class DeathAnimation:
    BROKEN_FLOOR_IMAGE = pygame.image.load("assets/broken-floor.png").convert_alpha()
    BROKEN_FLOOR_IMAGE = scale_by(BROKEN_FLOOR_IMAGE, 0.4)

    current_frame: pygame.Surface
    pos: pygame.Vector2

    def __init__(self, pos: pygame.Vector2) -> None:
        self.current_frame = self.BROKEN_FLOOR_IMAGE.copy()
        self.rect = self.current_frame.get_rect(center=pos)
        self.pos = self.rect.topleft
        self.alpha = 255
        self.shared = Shared()
        self.done = False

    def update(self):
        self.alpha -= 100 * self.shared.dt
        self.current_frame.set_alpha(self.alpha)
        if self.alpha <= 10:
            self.done = True


class Sword:
    IMAGES = load_scale_3("assets/bee_sword.png"), load_scale_3(
        "assets/centi_sword.png"
    )
    INITIAL_SPEED = 100
    ORIGINAL_AIM_IMAGE = pygame.image.load("assets/attack_area.png").convert_alpha()
    ORIGINAL_AIM_IMAGE = scale_by(ORIGINAL_AIM_IMAGE, 0.3)
    BOOM_SFX = pygame.mixer.Sound("assets/explosion.wav")

    def __init__(
        self, image_index: int, damage: int, target_pos: pygame.Vector2
    ) -> None:
        self.shared = Shared()
        self.image = self.IMAGES[image_index]
        self.damage = damage
        self.acceleration = 3.3
        self.speed = self.INITIAL_SPEED
        self.target = target_pos.copy()
        self.pos = pygame.Vector2(
            self.target.x - (self.image.get_width() / 2), self.target.y - 600
        )
        self.rect = self.image.get_rect(topleft=self.pos)
        self.active = False
        self.alive = True
        self.aiming = True
        self.wave = SinWave(0.03)
        self.aim_image = self.ORIGINAL_AIM_IMAGE.copy()
        self.aim_rect = self.aim_image.get_rect(center=self.target)
        self.aim_time = Time(2.5)

    def aim(self):
        self.aim_image = scale_by(self.ORIGINAL_AIM_IMAGE, 1 + (self.wave.val() * 0.12))
        self.aim_rect = self.aim_image.get_rect(center=self.target)

        if self.aim_time.tick():
            self.active = True
            self.aiming = False

    def move_on_attack(self):
        self.speed += self.acceleration
        self.pos.y += self.speed * self.shared.dt

        self.rect.topleft = self.pos

        if (
            self.aim_rect.colliderect(self.shared.player.rect)
            and self.rect.bottom >= self.target.y
        ):
            self.shared.player.modify_health(-self.damage)
            self.active = False

        if self.rect.bottom >= self.target.y:
            self.active = False

    def on_done(self):
        self.BOOM_SFX.play()
        self.shared.ss.add(1.5, 3.0)
        self.shared.play_it_once_anims.append(DeathAnimation(self.target))
        self.alive = False

    def update(self):
        if self.aiming:
            self.aim()
        elif self.active:
            self.move_on_attack()
        else:
            self.on_done()

    def draw(self):
        self.shared.screen.blit(
            self.aim_image, self.shared.camera.transform(self.aim_rect)
        )
        self.shared.screen.blit(self.image, self.shared.camera.transform(self.rect))
