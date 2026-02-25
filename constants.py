import typing as t
from collections import defaultdict

import pygame.color

from type import Coord, Pos, Ring, Player


def _build_axis_values() -> dict[Ring, tuple[float, float, float]]:
    _X_WORLD_LO = 1.0 / 15.0
    _X_WORLD_MI = 0.5
    _X_WORLD_HI = 1.0 - _X_WORLD_LO

    _Y_WORLD_LO = 16.0 / 75.0
    _Y_WORLD_MI = 0.5
    _Y_WORLD_HI = 1.0 - _Y_WORLD_LO

    _Z_WORLD_LO = 53.0 / 150.0
    _Z_WORLD_MI = 0.5
    _Z_WORLD_HI = 1.0 - _Z_WORLD_LO

    return {
        Ring.X: (_X_WORLD_LO, _X_WORLD_MI, _X_WORLD_HI),
        Ring.Y: (_Y_WORLD_LO, _Y_WORLD_MI, _Y_WORLD_HI),
        Ring.Z: (_Z_WORLD_LO, _Z_WORLD_MI, _Z_WORLD_HI),
    }


AXIS_VALUES = _build_axis_values()

LINE_WORLD_THICKNESS = (4 / 300)
DOT_WORLD_RADIUS = (4 / 300)
DOT_BORDER_WORLD_THICKNESS = (1.5 / 300)
PLAYER_WORLD_RADIUS = (8/300)

# Colors
LINE_COLOR = pygame.color.THECOLORS['black']
BOARD_BACKGROUND_COLOR = pygame.color.THECOLORS['white']
DOT_COLOR = pygame.color.THECOLORS['black']
DOT_BORDER_COLOR = pygame.color.THECOLORS['white']

PLAYER_COLOR: dict[Player, tuple[int, int, int, int]] = {
    Player.WHITE: pygame.color.THECOLORS['white'],
    Player.BLACK: pygame.color.THECOLORS['black'],
}

PLAYER_BORDER_COLOR = pygame.color.THECOLORS['darkgrey']
PLAYER_bORDER_WORLD_THICKNESS = (1.5 / 300)

def _build_coord_world_position():
    pos_order = {
        Pos.P1: (0, 0),  # LO, LO
        Pos.P2: (1, 0),  # MI, LO
        Pos.P3: (2, 0),  # HI, LO
        Pos.P4: (2, 1),  # HI, MI
        Pos.P5: (2, 2),  # HI, HI
        Pos.P6: (1, 2),  # MI, HI
        Pos.P7: (0, 2),  # LO, HI
        Pos.P8: (0, 1),  # LO, MI
    }
    coord_world_position: dict[Coord, tuple[float, float]] = {}

    for ring in Ring:
        axis_value = AXIS_VALUES[ring]
        for pos in Pos:
            coord = Coord(ring, pos)
            o1, o2 = pos_order[pos]
            a1, a2 = axis_value[o1], axis_value[o2]
            coord_world_position[coord] = (a1, a2)
    return coord_world_position

COORD_WORLD_POS: dict[Coord, tuple[float, float]] = _build_coord_world_position()


def _add_edge(edges: defaultdict[Coord, set[Coord]], coord_from: Coord, coord_to: Coord):
    es = edges[coord_from]
    es.add(coord_to)
    es = edges[coord_to]
    es.add(coord_from)


def _build_board_edges() -> dict[Coord, set[Coord]]:
    edges = defaultdict(set)
    ring_edges = {
        (Pos.P1, Pos.P2),
        (Pos.P2, Pos.P3),
        (Pos.P3, Pos.P4),
        (Pos.P4, Pos.P5),
        (Pos.P5, Pos.P6),
        (Pos.P6, Pos.P7),
        (Pos.P7, Pos.P8),
        (Pos.P8, Pos.P1)
    }

    mid_edges = {
        Pos.P2,
        Pos.P4,
        Pos.P6,
        Pos.P8
    }

    for ring in Ring:
        for p1, p2 in ring_edges:
            c1, c2 = Coord(ring, p1), Coord(ring, p2)
            _add_edge(edges, c1, c2)

    for r1, r2 in ((Ring.X, Ring.Y), (Ring.Y, Ring.Z)):
        for p in mid_edges:
            c1 = Coord(r1, p)
            c2 = Coord(r2, p)
            _add_edge(edges, c1, c2)
    return edges





# Edges
BOARD_EDGES: dict[Coord, set[Coord]] = _build_board_edges()
