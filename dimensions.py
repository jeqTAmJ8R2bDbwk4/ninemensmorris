import typing as t


OUTER_WORLD_LO: t.Final[float] = 1.0 / 15.0
OUTER_WORLD_MI: t.Final[float] = 0.5
OUTER_WORLD_HI: t.Final[float] = 1.0 - OUTER_WORLD_LO

MID_WORLD_LO: t.Final[float] = 16.0 / 75.0
MID_WORLD_MI: t.Final[float] = 0.5
MID_WORLD_HI: t.Final[float] = 1.0 - MID_WORLD_LO

INNER_WORLD_LO: t.Final[float] = 53.0 / 150.0
INNER_WORLD_MI: t.Final[float] = 0.5
INNER_WORLD_HI: t.Final[float] = 1.0 - INNER_WORLD_LO

LINE_THICKNESS: t.Final[float] = 1 / 75

DOT_RADIUS: t.Final[float] = 1 / 50
DOT_BORDER_THICKNESS: t.Final[float] = 1 / 200

PIECE_RADIUS: t.Final[float] = 2.5 / 75
PIECE_BORDER_THICKNESS: t.Final[float] = 1 / 500

HIGHLIGHT_BORDER_WIDTH: t.Final[float] = PIECE_RADIUS + 1 / 150
HIGHLIGHT_BORDER_THICKNESS: t.Final[float] = 1 / 300
HIGHLIGHT_BORDER_RADIUS: t.Final[float] = 1 / 75