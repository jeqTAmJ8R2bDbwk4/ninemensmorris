import math

import pygame

import constants
import type
from constants import COORD_WORLD_POS, LINE_WORLD_THICKNESS, LINE_COLOR, BOARD_BACKGROUND_COLOR, DOT_WORLD_RADIUS, DOT_BORDER_WORLD_THICKNESS, DOT_COLOR, DOT_BORDER_COLOR
from type import Coord, Ring, Pos, Board, Player

_RING_MILLS = [
    frozenset((Pos.P1, Pos.P2, Pos.P3)),
    frozenset((Pos.P3, Pos.P4, Pos.P5)),
    frozenset((Pos.P5, Pos.P6, Pos.P7)),
    frozenset((Pos.P7, Pos.P8, Pos.P1)),
]

_VERTICAL_MILL = frozenset((Pos.P2, Pos.P4, Pos.P6, Pos.P8))


def has_mill(board: Board, coord: Coord, player: Player) -> bool:
    assert board.get(coord, None) == player

    for ring_mill in _RING_MILLS:
        if coord.pos not in ring_mill:
            continue

        is_complete = all(board.get(Coord(coord.ring, pos), None) == player for pos in ring_mill)
        if is_complete:
            return True

    if coord.pos not in _VERTICAL_MILL:
        return False

    is_complete = all(board.get(Coord(ring, coord.pos), None) == player for ring in Ring)
    if is_complete:
        return True

    return False



def to_abs(value: float | tuple[float, float], size: int) -> float | tuple[float, float]:
    if isinstance(value, tuple):
        x, y = value
        x, y = to_abs(x, size), to_abs(y, size)
        return x, y
    return value * size


def draw_player(player: Player, size: int) -> pygame.Surface:
    color = constants.PLAYER_COLOR[player]
    border_thickness = to_abs(constants.PLAYER_bORDER_WORLD_THICKNESS, size)
    radius = to_abs(constants.PLAYER_WORLD_RADIUS, size)
    diameter = to_abs(2 * constants.PLAYER_WORLD_RADIUS, size)
    surface: pygame.Surface = pygame.surface.Surface((diameter, diameter), pygame.SRCALPHA)
    pygame.draw.circle(surface, color, (diameter // 2, diameter // 2), radius)
    pygame.draw.circle(surface, constants.PLAYER_BORDER_COLOR, (diameter // 2, diameter // 2), radius, width=int(border_thickness))

    return surface


def draw_highlight(size: int, time: float) -> pygame.Surface:
    diameter = to_abs(2 * constants.PLAYER_WORLD_RADIUS, size)
    surface: pygame.Surface = pygame.surface.Surface((diameter, diameter), pygame.SRCALPHA)
    alpha = max(min(int(round(((math.sin(time) + 1) * 0.25) + 0.5 * 255)), 255), 0)
    red = pygame.color.THECOLORS['red']
    red = *red[:3], alpha
    # print(red)
    rect = pygame.rect.Rect(0, 0, diameter, diameter)
    pygame.draw.rect(surface, red, rect, width=5)
    return surface



def draw_board_surface(board: type.Board, size: int) -> pygame.Surface:
    surface = pygame.Surface((size, size))
    surface.fill(BOARD_BACKGROUND_COLOR)

    line_thickness = int(to_abs(LINE_WORLD_THICKNESS, size))

    outer_dot_radius = to_abs(DOT_WORLD_RADIUS + DOT_BORDER_WORLD_THICKNESS, size)
    inner_dot_radius = to_abs(DOT_WORLD_RADIUS, size)

    absolute: dict[Coord, tuple[float, float]] = {}

    for ring in Ring:
        for pos in Pos:
            coord = Coord(ring, pos)
            absolute[coord] = to_abs(COORD_WORLD_POS[coord], size)

    edges: set[tuple[tuple[float, float], tuple[float, float]]] = set()

    for coord_from, coord_tos in constants.BOARD_EDGES.items():
        abs_from = absolute[coord_from]
        for coord_to in coord_tos:
            abs_to = absolute[coord_to]
            if (abs_to, abs_from) in edges:
                continue
            edges.add((abs_from, abs_to))

    for coord_from, coord_to in edges:
        pygame.draw.line(surface, LINE_COLOR, coord_from, coord_to, width=line_thickness)

    for ring in Ring:
        for pos in Pos:
            coord = Coord(ring, pos)
            pygame.draw.circle(surface, DOT_BORDER_COLOR, absolute[coord], outer_dot_radius)
            pygame.draw.circle(surface, DOT_COLOR, absolute[coord], inner_dot_radius)

    # print(board)
    for coord, player in board.items():
            highlight_surface = draw_player(player, size)
            x, y = constants.COORD_WORLD_POS[coord]
            x, y = to_abs((x, y), size)
            x -= highlight_surface.get_size()[0] // 2
            y -= highlight_surface.get_size()[1] // 2
            surface.blit(highlight_surface, (x, y))

    return surface

