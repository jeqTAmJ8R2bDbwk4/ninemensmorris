import enum
import typing as t

class Ring(enum.Enum):
    X = enum.auto()  # Outer
    Y = enum.auto()  # Mid
    Z = enum.auto()  # Inner

class Pos(enum.Enum):
    P1 = enum.auto()
    P2 = enum.auto()
    P3 = enum.auto()
    P4 = enum.auto()
    P5 = enum.auto()
    P6 = enum.auto()
    P7 = enum.auto()
    P8 = enum.auto()

class Coord(t.NamedTuple):
    ring: Ring
    pos: Pos

class Player(enum.Enum):
    WHITE = enum.auto()
    BLACK = enum.auto()

Board: t.TypeAlias = t.Dict[Coord, Player]
