import random
import time
from dataclasses import dataclass

from .shared import Shared
from .utils import Time


@dataclass
class ScreenShake:
    time: float
    magnitude: float

    def __post_init__(self):
        self.start = time.time()

    def create_offset(self):
        self.offset = (
            random.uniform(-1, 1) * self.magnitude,
            random.uniform(-1, 1) * self.magnitude,
        )


class ScreenShakeManager:
    def __init__(self) -> None:
        self.shared = Shared(ss=self)
        self.shakes: list[ScreenShake] = []

    def add(self, time: float, magnitude: float):
        self.shakes.append(ScreenShake(time, magnitude))

    def filter_shakes(self):
        for shake in self.shakes[:]:
            if time.time() - shake.start > shake.time:
                self.shakes.remove(shake)

    def order_shakes(self):
        self.shakes.sort(key=lambda shake: shake.magnitude)

    def apply_shakes(self):
        if not self.shakes:
            return

        self.shakes[-1].create_offset()
        self.shared.camera.offset += self.shakes[-1].offset

    def update(self):
        self.filter_shakes()
        self.order_shakes()
        self.apply_shakes()
