import pygame
from logit import log

from .shared import Shared


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.shared = Shared()
        self.win_init()

        from .cursor import Cursor
        from .states import StateManager
        from .widgets import Widgets

        self.shared.cursor = Cursor()
        self.state_manager = StateManager()
        self.shared.widgets = Widgets()

        log.config(rotation_space="5kb")

    def win_init(self):
        self.shared.screen = pygame.display.set_mode(
            self.shared.SCRECT.size, pygame.NOFRAME
        )
        self.clock = pygame.time.Clock()

    def _update(self):
        self.shared.events = pygame.event.get()
        self.shared.mouse_press = pygame.mouse.get_pressed()
        self.shared.dt = self.clock.tick() / 1000

        self.shared.cursor.update()
        self.state_manager.update()
        self.shared.widgets.update()

    def _draw(self):
        self.shared.screen.fill("black")
        self.state_manager.draw()
        self.shared.cursor.draw()
        self.shared.widgets.draw()

        pygame.display.flip()

    def run(self):
        while True:
            self._update()
            self._draw()


def main():
    game = Game()
    game.run()
