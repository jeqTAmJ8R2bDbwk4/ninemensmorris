import functools
import typing as t

import pygame

import dimensions
import utils
import models
import colors
from models import Player


P = t.ParamSpec("P")

def supersampling(
    func: t.Callable[P, pygame.Surface],
) -> t.Callable[P, pygame.Surface]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> pygame.Surface:
        if "scale" not in kwargs:
            raise TypeError("Missing required 'scale' keyword argument")

        original_scale = kwargs["scale"]
        if not isinstance(original_scale, int):
            raise TypeError("'scale' must be int")

        kwargs["scale"] = original_scale * 2
        surface = func(*args, **kwargs)

        return pygame.transform.smoothscale_by(surface, 0.5)

    return wrapper


@supersampling
def draw_player(player: models.Player, *, scale: int) -> pygame.Surface:
    radius = utils.pixel(dimensions.PIECE_RADIUS, scale)
    diameter = utils.pixel(2 * dimensions.PIECE_RADIUS, scale)
    border_thickness = utils.pixel(dimensions.PIECE_BORDER_THICKNESS, scale)

    size = (diameter, diameter)
    center = (radius, radius)

    piece_color = utils.PIECE_COLORS[player]
    piece_border_color = utils.PIECE_BORDER_COLORS[player]

    surface = pygame.surface.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(surface, piece_color, center, radius)

    pygame.draw.circle(surface, piece_border_color, center, (1 * radius) // 5, width=border_thickness)
    pygame.draw.circle(surface, piece_border_color, center, (2 * radius) // 5, width=border_thickness)
    pygame.draw.circle(surface, piece_border_color, center, (3 * radius) // 5, width=border_thickness)
    pygame.draw.circle(surface, piece_border_color, center, (4 * radius) // 5, width=border_thickness)
    pygame.draw.circle(surface, piece_border_color, center, (5 * radius) // 5, width=border_thickness)

    return surface

@supersampling
def draw_board_dot(*, scale: int) -> pygame.Surface:
    radius = utils.pixel(dimensions.DOT_RADIUS, scale)
    border_thickness = utils.pixel(dimensions.DOT_BORDER_THICKNESS, scale)
    diameter = utils.pixel(2 * (dimensions.DOT_RADIUS + dimensions.DOT_BORDER_THICKNESS) , scale)

    size = (diameter, diameter)
    center = (radius+border_thickness, radius+border_thickness)

    surface = pygame.surface.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(surface, colors.BOARD_DOT_COLOR, center, radius)
    pygame.draw.circle(surface, colors.BOARD_DOT_BORDER_COLOR, center, radius, width=border_thickness)

    return surface

@supersampling
def draw_highlight(*, scale: int) -> pygame.Surface:
    diameter = utils.pixel(2 * dimensions.HIGHLIGHT_BORDER_WIDTH, scale)
    border_thickness = utils.pixel(dimensions.HIGHLIGHT_BORDER_THICKNESS, scale)
    border_radius = utils.pixel(dimensions.HIGHLIGHT_BORDER_RADIUS, scale)

    rect = pygame.rect.Rect(0, 0, diameter, diameter)

    surface = pygame.surface.Surface((diameter, diameter), pygame.SRCALPHA)
    pygame.draw.rect(surface, colors.HIGHLIGHT, rect, width=border_thickness, border_radius=border_radius)
    return surface


def draw_game_board_surface(
        scale: int,
        game_board: models.GameBoard,
        highlighted: set[models.Coordinate],
) -> pygame.Surface:
    size = (scale, scale)

    surface = pygame.Surface(size)
    surface.fill(colors.BOARD_BACKGROUND_COLOR)

    line_thickness = utils.pixel(dimensions.LINE_THICKNESS, scale)

    board_dot = draw_board_dot(scale=scale)
    player = {
        Player.WHITE: draw_player(Player.WHITE, scale=scale),
        Player.BLACK: draw_player(Player.BLACK, scale=scale),
    }
    highlight = draw_highlight(scale=scale)

    coordinate_dest = {}
    for start_coordinate, (x, y) in utils.COORDINATE_DEST.items():
        coordinate_dest[start_coordinate] = (utils.pixel(x, scale), utils.pixel(y, scale))

    drawn_edges = set()
    for start_coordinate, neighbors in utils.COORDINATE_NEIGHBORS.items():
        start = coordinate_dest[start_coordinate]
        for end_coordinate in neighbors:
            if (start_coordinate, end_coordinate) in drawn_edges:
                continue
            drawn_edges.add((end_coordinate, start_coordinate))

            end = coordinate_dest[end_coordinate]
            pygame.draw.line(surface, colors.BOARD_LINE_COLOR, start, end, width=line_thickness)

    blit_sequence = []
    for ring in models.Ring:
        for position in models.Position:
            coordinate = models.Coordinate(ring, position)
            dest = coordinate_dest[coordinate]
            dest = utils.center_dest(dest, board_dot.get_size())
            blit_sequence.append((board_dot, dest))

    for coordinate, p in game_board.items():
        if p is None:
            continue

        dest = coordinate_dest[coordinate]
        dest = utils.center_dest(dest, player[p].get_size())
        blit_sequence.append((player[p], dest))

    for coordinate in highlighted:
        dest = coordinate_dest[coordinate]
        dest = utils.center_dest(dest, highlight.get_size())
        blit_sequence.append((highlight, dest))

    surface.blits(blit_sequence)

    return surface
