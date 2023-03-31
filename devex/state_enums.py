from enum import Enum, auto


class State(Enum):
    MENU = auto()
    TUTORIAL = auto()
    GAME = auto()
    GAME_OVER = auto()
    VICTORY = auto()
