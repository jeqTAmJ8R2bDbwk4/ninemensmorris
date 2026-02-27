import typing as t
from collections import defaultdict

import pygame

import dimensions
import models
import colors

from models import Ring


def _build_piece_colors() -> dict[models.Player, models.Color]:
    return {
        models.Player.WHITE: colors.PIECE_WHITE,
        models.Player.BLACK: colors.PIECE_BLACK,
    }

PIECE_COLORS: t.Final = _build_piece_colors()


def _build_piece_border_colors() -> dict[models.Player, models.Color]:
    return {
        models.Player.WHITE: colors.PIECE_WHITE_BORDER,
        models.Player.BLACK: colors.PIECE_BLACK_BORDER,
    }

PIECE_BORDER_COLORS: t.Final = _build_piece_border_colors()


def _build_ring_axis_values() -> dict[tuple[models.Ring, models.AxisLevel], float]:
    return {
        (models.Ring.OUTER, models.AxisLevel.LO): dimensions.OUTER_WORLD_LO,
        (models.Ring.OUTER, models.AxisLevel.MI): dimensions.OUTER_WORLD_MI,
        (models.Ring.OUTER, models.AxisLevel.HI): dimensions.OUTER_WORLD_HI,
        (models.Ring.MIDDLE, models.AxisLevel.LO): dimensions.MID_WORLD_LO,
        (models.Ring.MIDDLE, models.AxisLevel.MI): dimensions.MID_WORLD_MI,
        (models.Ring.MIDDLE, models.AxisLevel.HI): dimensions.MID_WORLD_HI,
        (models.Ring.INNER, models.AxisLevel.LO): dimensions.INNER_WORLD_LO,
        (models.Ring.INNER, models.AxisLevel.MI): dimensions.INNER_WORLD_MI,
        (models.Ring.INNER, models.AxisLevel.HI): dimensions.INNER_WORLD_HI,
    }

_RING_AXIS_VALUES: t.Final = _build_ring_axis_values()


def _build_position_axis_levels() -> dict[models.Position, tuple[models.AxisLevel, models.AxisLevel]]:
    return {
        models.Position.P1: (models.AxisLevel.LO, models.AxisLevel.LO),  # LO, LO
        models.Position.P2: (models.AxisLevel.MI, models.AxisLevel.LO),  # MI, LO
        models.Position.P3: (models.AxisLevel.HI, models.AxisLevel.LO),  # HI, LO
        models.Position.P4: (models.AxisLevel.HI, models.AxisLevel.MI),  # HI, MI
        models.Position.P5: (models.AxisLevel.HI, models.AxisLevel.HI),  # HI, HI
        models.Position.P6: (models.AxisLevel.MI, models.AxisLevel.HI),  # MI, HI
        models.Position.P7: (models.AxisLevel.LO, models.AxisLevel.HI),  # LO, HI
        models.Position.P8: (models.AxisLevel.LO, models.AxisLevel.MI),  # LO, MI
    }

_POSITION_AXIS_LEVELS: t.Final = _build_position_axis_levels()


def _build_coordinate_xy() -> dict[models.Coordinate, tuple[float, float]]:
    coordinate_xy = {}

    for ring in models.Ring:
        for position in models.Position:
            coord = models.Coordinate(ring, position)
            axis_level_x, axis_level_y = _POSITION_AXIS_LEVELS[position]
            x, y = _RING_AXIS_VALUES[ring, axis_level_x], _RING_AXIS_VALUES[ring, axis_level_y]
            coordinate_xy[coord] = x, y

    return coordinate_xy

COORDINATE_DEST: t.Final = _build_coordinate_xy()


def _build_ring_neighbors() -> tuple[tuple[models.Position, models.Position], ...]:
    return (
        (models.Position.P1, models.Position.P2),
        (models.Position.P2, models.Position.P3),
        (models.Position.P3, models.Position.P4),
        (models.Position.P4, models.Position.P5),
        (models.Position.P5, models.Position.P6),
        (models.Position.P6, models.Position.P7),
        (models.Position.P7, models.Position.P8),
        (models.Position.P8, models.Position.P1)
    )

_RING_NEIGHBORS: t.Final = _build_ring_neighbors()


def _build_vertical_positions() -> tuple[models.Position, ...]:
    return (
        models.Position.P2,
        models.Position.P4,
        models.Position.P6,
        models.Position.P8
    )

_VERTICAL_POSITIONS: t.Final = _build_vertical_positions()


def _build_vertical_ring_pairs() -> tuple[tuple[models.Ring, models.Ring], ...]:
    return (
        (models.Ring.OUTER, models.Ring.MIDDLE),
        (models.Ring.MIDDLE, models.Ring.INNER)
    )

_VERTICAL_RING_PAIRS: t.Final = _build_vertical_ring_pairs()


def _connect_coordinates(
        edges: defaultdict[models.Coordinate, set[models.Coordinate]],
        coord_from: models.Coordinate,
        coord_to: models.Coordinate
) -> None:
    edges[coord_from].add(coord_to)
    edges[coord_to].add(coord_from)

def _build_coordinate_neighbors() -> dict[models.Coordinate, set[models.Coordinate]]:
    edges = defaultdict(set)

    for ring in models.Ring:
        for position_1, position_2 in _RING_NEIGHBORS:
            coordinate_1, coordinate_2 = models.Coordinate(ring, position_1), models.Coordinate(ring, position_2)
            _connect_coordinates(edges, coordinate_1, coordinate_2)

    for ring_1, ring_2 in _VERTICAL_RING_PAIRS:
        for position in _VERTICAL_POSITIONS:
            coordinate_1 = models.Coordinate(ring_1, position)
            coordinate_2 = models.Coordinate(ring_2, position)
            _connect_coordinates(edges, coordinate_1, coordinate_2)
    return edges

COORDINATE_NEIGHBORS: t.Final = _build_coordinate_neighbors()


def _build_ring_mill_positions() -> tuple[set[models.Position], ...]:
    return (
        {models.Position.P1, models.Position.P2, models.Position.P3},
        {models.Position.P3, models.Position.P4, models.Position.P5},
        {models.Position.P5, models.Position.P6, models.Position.P7},
        {models.Position.P7, models.Position.P8, models.Position.P1},
    )

_RING_MILL_POSITIONS: t.Final = _build_ring_mill_positions()


def _build_mill_neighbors() -> dict[models.Coordinate, list[list[models.Coordinate]]]:
    mill_neighbors = defaultdict(list)
    for ring in models.Ring:
        for position in models.Position:
            coordinate = models.Coordinate(ring, position)
            for positions in _RING_MILL_POSITIONS:
                if coordinate.position not in positions:
                    continue

                mill_neighbors[coordinate].append([models.Coordinate(ring=ring, position=position) for position in positions])

            if coordinate.position not in _VERTICAL_POSITIONS:
                continue

            mill_neighbors[coordinate].append([models.Coordinate(ring=ring, position=coordinate.position) for ring in Ring])
    return mill_neighbors

MILL_NEIGHBORS: t.Final = _build_mill_neighbors()


def center_dest(
        dest: tuple[int, int],
        size: tuple[int, int],
) -> tuple[int, int]:
    x, y = dest
    width, height = size
    return x - width // 2, y - height // 2


def pixel(dim: float, scale: int) -> int:
    assert dim > 0
    assert scale > 0
    return int(round(dim * scale))