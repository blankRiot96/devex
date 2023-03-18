from .state_enums import State
from .shared import Shared


class MenuState:
    def __init__(self) -> None:
        self.next_state = None
        self.shared = Shared()

    def update(self):
        ...

    def draw(self):
        ...
