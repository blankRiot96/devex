import asyncio

import pygame

from .shared import Shared


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.shared = Shared()
        self.win_init()

        from .states import StateManager

        self.state_manager = StateManager()

    def win_init(self):
        self.shared.screen = pygame.display.set_mode(
            self.shared.SCRECT.size, pygame.NOFRAME
        )
        self.clock = pygame.time.Clock()

    def _update(self):
        self.shared.events = pygame.event.get()
        self.shared.mouse_press = pygame.mouse.get_pressed()
        self.shared.dt = self.clock.tick() / 1000
        self.shared.dt = min(self.shared.dt, 0.1)

        self.state_manager.update()

    def _draw(self):
        self.shared.screen.fill("black")
        self.state_manager.draw()

        pygame.display.flip()

    async def run(self):
        while True:
            self._update()
            self._draw()

            await asyncio.sleep(0)


def main():
    game = Game()
    asyncio.run(game.run())
