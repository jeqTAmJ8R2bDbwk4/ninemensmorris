import typing as t

import pygame

import dimensions
import models
import utils
import assets
from models import Coordinate, Position, Player, Ring



def _is_pressed_coordinate(
    mouse_pos: tuple[int, int],
    window_size: tuple[int, int],
    scale: int,
    coordinates: set[Coordinate],
) -> Coordinate | None:
    width, height = window_size
    mx, my = mouse_pos

    highlight_width = utils.pixel(dimensions.HIGHLIGHT_BORDER_WIDTH, scale)

    board_offset_x = (width - scale) // 2
    board_offset_y = (height - scale) // 2

    for coordinate in coordinates:
        x, y = utils.COORDINATE_DEST[coordinate]
        px = utils.pixel(x, scale)
        py = utils.pixel(y, scale)

        dest_x, dest_y = utils.center_dest(
            (px, py),
            (highlight_width, highlight_width),
        )

        rect = pygame.Rect(
            dest_x + board_offset_x,
            dest_y + board_offset_y,
            highlight_width,
            highlight_width,
        )

        if rect.collidepoint(mx, my):
            return coordinate

    return None



class PlacementGameState(models.GameState):
    def update(self, surface: pygame.Surface, events: t.Iterable[pygame.event.Event]) -> models.GameState:
        next_state = self

        size = surface.get_size()
        width, height = size
        scale = min(size)

        highlighted_coordinates = {coordinate for (coordinate, player) in self._game_board.items() if player is None}

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                pressed_coord = _is_pressed_coordinate(pos, size, scale, highlighted_coordinates)
                if pressed_coord is None:
                    continue
                self._game_board[pressed_coord] = self._player
                self._left_pieces[self._player] -= 1
                assert self._left_pieces[self._player] >= 0

                has_mill = any(all(self._game_board[neighbor] == self._player for neighbor in neighbors) for neighbors in utils.MILL_NEIGHBORS[pressed_coord])
                if has_mill:
                    return RemoveGameState(self._player, self._game_board, self._left_pieces)

                next_player = models.Player.switch(self._player)
                if self._left_pieces[next_player] == 0:
                    return MovementSelectGameState(next_player, self._game_board, self._left_pieces)
                else:
                    return PlacementGameState(next_player, self._game_board, self._left_pieces)


        game_board = assets.draw_game_board_surface(scale, self._game_board, highlighted_coordinates)
        player = assets.draw_player(self._player, scale=scale)

        game_board_dest = width // 2, height // 2
        game_board_dest = utils.center_dest(game_board_dest, game_board.get_size())

        player_dest = pygame.mouse.get_pos()
        player_dest = utils.center_dest(player_dest, player.get_size())

        surface.blit(game_board, game_board_dest)
        surface.blit(player, player_dest)

        return next_state

    def __init__(self, player: models.Player, game_board: models.GameBoard, left_pieces: models.LeftPieces) -> None:
        print(type(self))
        self._player = player
        self._game_board = game_board
        self._left_pieces = left_pieces




class MovementSelectGameState(models.GameState):
    def update(self, surface: pygame.Surface, events: t.Iterable[pygame.event.Event]) -> models.GameState:
        size = surface.get_size()
        width, height = size
        scale = min(size)

        highlighted_coordinates = {coordinate for (coordinate, player) in self._game_board.items() if player == self._player}

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                pressed_coord = _is_pressed_coordinate(pos, size, scale, highlighted_coordinates)
                if pressed_coord is None:
                    continue
                self._game_board[pressed_coord] = None
                return MovementMoveGameState(self._player, self._game_board, self._left_pieces, pressed_coord)


        game_board = assets.draw_game_board_surface(scale, self._game_board, highlighted_coordinates)

        game_board_dest = width // 2, height // 2
        game_board_dest = utils.center_dest(game_board_dest, game_board.get_size())

        surface.blit(game_board, game_board_dest)

        return self

    def __init__(self, player: models.Player, game_board: models.GameBoard, left_pieces: models.LeftPieces) -> None:
        print(type(self))

        self._player = player
        self._game_board = game_board
        self._left_pieces = left_pieces




class MovementMoveGameState(models.GameState):
    def update(self, surface: pygame.Surface, events: t.Iterable[pygame.event.Event]) -> models.GameState:
        size = surface.get_size()
        width, height = size
        scale = min(size)

        highlighted_coordinates = {coordinate for (coordinate, player) in self._game_board.items() if player is None and coordinate in utils.COORDINATE_NEIGHBORS[self._src_coordinate]}

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                pressed_coord = _is_pressed_coordinate(pos, size, scale, highlighted_coordinates)
                if pressed_coord is None:
                    self._game_board[self._src_coordinate] = self._player
                    return MovementSelectGameState(self._player, self._game_board, self._left_pieces)
                self._game_board[pressed_coord] = self._player
                has_mill = any(all(self._game_board[neighbor] == self._player for neighbor in neighbors) for neighbors in utils.MILL_NEIGHBORS[pressed_coord])
                if has_mill:
                    return RemoveGameState(self._player, self._game_board, self._left_pieces)

                next_player = models.Player.switch(self._player)

                if self._left_pieces[next_player] == 0:
                    return MovementSelectGameState(next_player, self._game_board, self._left_pieces)
                return PlacementGameState(next_player, self._game_board, self._left_pieces)

        game_board = assets.draw_game_board_surface(scale, self._game_board, highlighted_coordinates)
        player = assets.draw_player(self._player, scale=scale)

        game_board_dest = width // 2, height // 2
        game_board_dest = utils.center_dest(game_board_dest, game_board.get_size())

        player_dest = pygame.mouse.get_pos()
        player_dest = utils.center_dest(player_dest, player.get_size())

        surface.blit(game_board, game_board_dest)
        surface.blit(player, player_dest)

        return self

    def __init__(self, player: models.Player, game_board: models.GameBoard, left_pieces: models.LeftPieces, src_coordinate: models.Coordinate) -> None:
        print(type(self))
        self._player = player
        self._game_board = game_board
        self._left_pieces = left_pieces
        self._src_coordinate = src_coordinate



class RemoveGameState(models.GameState):
    def update(self, surface: pygame.Surface, events: t.Iterable[pygame.event.Event]) -> models.GameState:
        size = surface.get_size()
        width, height = size
        scale = min(size)

        highlighted_coordinates = {coordinate for (coordinate, player) in self._game_board.items() if player is not None and player != self._player}

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                pressed_coord = _is_pressed_coordinate(pos, size, scale, highlighted_coordinates)
                if pressed_coord is None:
                    continue
                self._game_board[pressed_coord] = None
                next_player = models.Player.switch(self._player)
                if self._left_pieces[next_player] == 0:
                    return MovementSelectGameState(next_player, self._game_board, self._left_pieces)
                return PlacementGameState(next_player, self._game_board, self._left_pieces)

        game_board = assets.draw_game_board_surface(scale, self._game_board, highlighted_coordinates)

        game_board_dest = width // 2, height // 2
        game_board_dest = utils.center_dest(game_board_dest, game_board.get_size())

        surface.blit(game_board, game_board_dest)

        return self

    def __init__(self, player: models.Player, game_board: models.GameBoard, left_pieces: models.LeftPieces) -> None:
        print(type(self))
        self._player = player
        self._game_board = game_board
        self._left_pieces = left_pieces
        print(type(self))
