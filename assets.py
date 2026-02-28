import functools
import typing as t

import pygame
import pygame.freetype
import pygame.gfxdraw

import dimensions
import utils
import models
import colors
from models import Player


P = t.ParamSpec("P")


_scale: int | None = None


def _supersampling(
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


def _render_shadow_hover(*, scale: int) -> pygame.Surface:
    blur_radius = 20
    radius = utils.pixel(dimensions.PIECE_SHADOW_HOVER_RADIUS, scale)
    diameter = utils.pixel(2 * dimensions.PIECE_SHADOW_HOVER_RADIUS, scale) + 3 * blur_radius
    size = (diameter, diameter)
    rect = pygame.rect.Rect(0, 0, *size)

    surface = pygame.surface.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(
        surface,
        (0, 0, 0, 60),
        rect.center,
        radius,
    )
    return pygame.transform.gaussian_blur(surface, blur_radius)


@_supersampling
def _render_player_hover(player: models.Player, *, scale: int) -> pygame.Surface:
    radius = utils.pixel(dimensions.PIECE_HOVER_RADIUS, scale)
    border_thickness = utils.pixel(dimensions.PIECE_HOVER_BORDER_THICKNESS, scale)

    piece_color = utils.PIECE_HOVER_COLORS[player]
    piece_border_color = utils.PIECE_HOVER_BORDER_COLORS[player]

    surface = _render_shadow_hover(scale=scale)
    center = surface.get_rect().center

    pygame.draw.circle(surface, piece_color, center, radius)

    pygame.draw.circle(surface, piece_border_color, center, (1 * radius) // 5, width=border_thickness)
    pygame.draw.circle(surface, piece_border_color, center, (2 * radius) // 5, width=border_thickness)
    pygame.draw.circle(surface, piece_border_color, center, (3 * radius) // 5, width=border_thickness)
    pygame.draw.circle(surface, piece_border_color, center, (4 * radius) // 5, width=border_thickness)
    pygame.draw.circle(surface, piece_border_color, center, (5 * radius) // 5, width=border_thickness)

    return surface


def _render_shadow(*, scale: int) -> pygame.Surface:
    blur_radius = 10
    radius = utils.pixel(dimensions.PIECE_SHADOW_RADIUS, scale)
    diameter = utils.pixel(2 * dimensions.PIECE_SHADOW_RADIUS, scale) + 3 * blur_radius
    size = (diameter, diameter)
    rect = pygame.rect.Rect(0, 0, *size)

    surface = pygame.surface.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(
        surface,
        (0, 0, 0, 100),
        rect.center,
        radius,
    )
    return pygame.transform.gaussian_blur(surface, blur_radius)


@_supersampling
def _render_player(player: models.Player, *, scale: int) -> pygame.Surface:
    radius = utils.pixel(dimensions.PIECE_RADIUS, scale)
    border_thickness = utils.pixel(dimensions.PIECE_BORDER_THICKNESS, scale)

    piece_color = utils.PIECE_COLORS[player]
    piece_border_color = utils.PIECE_BORDER_COLORS[player]

    surface = _render_shadow(scale=scale)
    center = surface.get_rect().center

    pygame.draw.circle(surface, piece_color, center, radius)

    for i in range(1, 6):
        pygame.draw.circle(surface, piece_border_color, center, (i * radius) // 5, width=border_thickness)

    return surface

@_supersampling
def _render_board_dot(*, scale: int) -> pygame.Surface:
    radius = utils.pixel(dimensions.DOT_RADIUS, scale)
    border_thickness = utils.pixel(dimensions.DOT_BORDER_THICKNESS, scale)
    diameter = utils.pixel(2 * (dimensions.DOT_RADIUS + dimensions.DOT_BORDER_THICKNESS) , scale)

    size = (diameter, diameter)
    center = (radius+border_thickness, radius+border_thickness)

    surface = pygame.surface.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(surface, colors.BOARD_DOT_COLOR, center, radius)
    pygame.draw.circle(surface, colors.BOARD_DOT_BORDER_COLOR, center, radius, width=border_thickness)

    return surface

@_supersampling
def _render_highlight(is_delete: bool, *, scale: int) -> pygame.Surface:
    diameter = utils.pixel(dimensions.HIGHLIGHT_BORDER_WIDTH, scale)
    border_thickness = utils.pixel(dimensions.HIGHLIGHT_BORDER_THICKNESS, scale)
    border_radius = utils.pixel(dimensions.HIGHLIGHT_BORDER_RADIUS, scale)
    color = colors.DELETE_HIGHLIGHT if is_delete else colors.PLACE_HIGHLIGHT

    rect = pygame.rect.Rect(0, 0, diameter, diameter)

    surface = pygame.surface.Surface((diameter, diameter), pygame.SRCALPHA)
    pygame.draw.rect(surface, color, rect, width=border_thickness, border_radius=border_radius)
    return surface


def render_game_board_surface(
        game_board: models.GameBoard,
        highlighted: set[models.Coordinate],
        *,
        scale: int,
        blacklist: set[models.Coordinate] | None = None,
        is_delete: bool = False
) -> pygame.Surface:
    if blacklist is None:
        blacklist = {}
    assert blacklist is not None

    size = (scale, scale)

    surface = pygame.Surface(size)
    surface.fill(colors.BOARD_BACKGROUND_COLOR)

    line_thickness = utils.pixel(dimensions.LINE_THICKNESS, scale)

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
            dest = utils.center_dest(dest, board_dot_surface.get_size())
            blit_sequence.append((board_dot_surface, dest))

    for coordinate, p in game_board.items():
        if coordinate in blacklist:
            continue

        if p is None:
            continue

        dest = coordinate_dest[coordinate]
        dest = utils.center_dest(dest, player_surface[p].get_size())
        blit_sequence.append((player_surface[p], dest))

    highlight = delete_highlight_surface if is_delete else place_highlight_surface

    for coordinate in highlighted:
        dest = coordinate_dest[coordinate]
        dest = utils.center_dest(dest, highlight.get_size())
        blit_sequence.append((highlight, dest))

    surface.blits(blit_sequence)

    return surface


def _small_font(*, scale: int) -> pygame.freetype.Font:
    size = utils.pixel(dimensions.CURRENT_FONT_SIZE, scale)
    font = pygame.freetype.Font("Roboto-Black.ttf", size)
    return font



def set_scale(scale: int):
    global shadow_hover_surface, player_hover_surface, shadow_surface, player_surface, board_dot_surface, place_highlight_surface, delete_highlight_surface, small_font
    shadow_hover_surface = _render_shadow_hover(scale=scale)
    player_hover_surface = {player_surface: _render_player_hover(player_surface, scale=scale) for player_surface in models.Player}
    shadow_surface = _render_shadow(scale=scale)
    player_surface = {player_surface: _render_player(player_surface, scale=scale) for player_surface in models.Player}
    board_dot_surface = _render_board_dot(scale=scale)
    place_highlight_surface = _render_highlight(is_delete=False, scale=scale)
    delete_highlight_surface = _render_highlight(is_delete=True, scale=scale)
    small_font = _small_font(scale=scale)



shadow_hover_surface: pygame.Surface | None = None
player_hover_surface: dict[models.Player, pygame.Surface] | None = None
shadow_surface: pygame.Surface | None = None
player_surface: dict[models.Player, pygame.Surface] | None = None
board_dot_surface: pygame.Surface | None = None
place_highlight_surface: pygame.Surface | None = None
delete_highlight_surface: pygame.Surface | None = None
small_font: pygame.freetype.Font | None = None

