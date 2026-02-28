import enum
import typing as t
import abc

import pygame


class Ring(enum.Enum):
    OUTER = enum.auto()
    MIDDLE = enum.auto()
    INNER = enum.auto()


class Position(enum.Enum):
    P1 = enum.auto()  # Top left, continue clock wise
    P2 = enum.auto()
    P3 = enum.auto()
    P4 = enum.auto()
    P5 = enum.auto()
    P6 = enum.auto()
    P7 = enum.auto()
    P8 = enum.auto()


class Coordinate(t.NamedTuple):
    ring: Ring
    position: Position


class Player(enum.Enum):
    WHITE = enum.auto()
    BLACK = enum.auto()

    def switch(self) -> t.Self:
        if self == self.WHITE:
            return self.BLACK
        elif self == self.BLACK:
            return self.WHITE
        else:
            assert False


class MouseClick(enum.Enum):
    UP = enum.auto()
    DOWN = enum.auto()


class AxisLevel(enum.Enum):
    LO = enum.auto()
    MI = enum.auto()
    HI = enum.auto()


GameBoard: t.TypeAlias = t.Dict[Coordinate, Player | None]
Color: t.TypeAlias = t.Tuple[int, int, int, int]
LeftPieces: t.TypeAlias = t.Dict[Player, int]


class GameState(enum.Enum):
    PLACEMENT = enum.auto()
    SELECT = enum.auto()
    MOVEMENT = enum.auto()
    REMOVE = enum.auto()
    FLY = enum.auto()


class Screen[T](metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def update(self, surface: pygame.Surface, events: t.Iterable[pygame.event.Event]) -> T | None:
        pass