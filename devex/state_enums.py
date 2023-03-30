from enum import Enum, auto


class State(Enum):
    GAME = auto()
    MENU = auto()
    GAME_OVER = auto()
    VICTORY = auto()
