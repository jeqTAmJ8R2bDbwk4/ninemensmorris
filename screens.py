import typing as t
import json

import pygame

import dimensions
import models
import utils
import assets
from models import Coordinate, Position, Player, Ring



class GameScreen(models.Screen[models.Player]):
    @classmethod
    def _is_pressed_coordinate(
            cls,
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

    def update(self, surface: pygame.Surface, events: t.Iterable[pygame.event.Event]) -> models.Player | None:
        size = surface.get_size()
        width, height = size
        scale = min(size)
        winner: models.Player | None = None

        if self._game_state == models.GameState.PLACEMENT:
            highlighted_coordinates = {
                coordinate
                for (coordinate, player) in self._game_board.items()
                if player is None
            }
        elif self._game_state == models.GameState.SELECT:
            remaining = sum(player == self._player for _, player in self._game_board.items())
            assert remaining >= 2
            highlighted_coordinates = {
                coordinate
                for (coordinate, player) in self._game_board.items()
                if player == self._player and (remaining <= 3 or any(self._game_board[c] is None for c in utils.COORDINATE_NEIGHBORS[coordinate]))
            }
        elif self._game_state == models.GameState.MOVEMENT:
            assert self._move_coordinate is not None
            highlighted_coordinates = {
                coordinate
                for (coordinate, player) in self._game_board.items()
                if player is None and coordinate in utils.COORDINATE_NEIGHBORS[self._move_coordinate]
            }
        elif self._game_state == models.GameState.FLY:
            highlighted_coordinates = {
                coordinate
                for (coordinate, player) in self._game_board.items()
                if player is None
            }
        elif self._game_state == models.GameState.REMOVE:
            highlighted_coordinates = {
                coordinate
                for (coordinate, player) in self._game_board.items()
                if player == self._player.switch()
            }
        else:
            assert False

        mouse_pos = pygame.mouse.get_pos()

        mouse_click: models.MouseClick | None = None
        hover_coordinate = self._is_pressed_coordinate(mouse_pos, size, scale, highlighted_coordinates)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = models.MouseClick.DOWN

            if event.type == pygame.MOUSEBUTTONUP:
                mouse_click = models.MouseClick.UP

        if mouse_click == models.MouseClick.DOWN and (self._game_state == models.GameState.PLACEMENT) and hover_coordinate is not None:
            self._game_board[hover_coordinate] = self._player
            self._left_pieces[self._player] -= 1
            assert self._left_pieces[self._player] >= 0

            has_mill = any(
                all(self._game_board[neighbor] == self._player for neighbor in neighbors)
                for neighbors in utils.MILL_NEIGHBORS[hover_coordinate]
            )

            if has_mill:
                self._game_state = models.GameState.REMOVE
                print(f"{self._game_state = }")
            else:
                self._player = self._player.switch()
                if self._left_pieces[self._player] > 0:
                    self._game_state = models.GameState.PLACEMENT
                    print(f"{self._game_state = }")
                elif self._left_pieces[self._player] == 0:
                    self._game_state = models.GameState.SELECT
                    print(f"{self._game_state = }")
                else:
                    assert False

        elif mouse_click == models.MouseClick.DOWN and (self._game_state == models.GameState.SELECT) and hover_coordinate is not None:
            self._move_coordinate = hover_coordinate

            remaining = sum(player == self._player for _, player in self._game_board.items())
            if remaining > 3:
                self._game_state = models.GameState.MOVEMENT
            elif remaining == 3:
                self._game_state = models.GameState.FLY
            else:
                assert False
            print(f"{self._game_state = }")

        elif mouse_click == models.MouseClick.UP and (self._game_state == models.GameState.MOVEMENT or self._game_state == models.GameState.FLY):
            if hover_coordinate is None:
                self._move_coordinate = None
                self._game_state = models.GameState.SELECT
                print(f"{self._game_state = }")
            else:
                self._game_board[self._move_coordinate] = None
                self._move_coordinate = None
                self._game_board[hover_coordinate] = self._player

                has_mill = any(
                    all(self._game_board[neighbor] == self._player for neighbor in neighbors)
                    for neighbors
                    in utils.MILL_NEIGHBORS[hover_coordinate]
                )
                print(has_mill)

                if has_mill:
                    self._game_state = models.GameState.REMOVE
                    print(f"{self._game_state = }")
                else:
                    self._player = self._player.switch()
                    if self._left_pieces[self._player] > 0:
                        self._game_state = models.GameState.PLACEMENT
                        print(f"{self._game_state = }")
                    elif self._left_pieces[self._player] == 0:
                        self._game_state = models.GameState.SELECT
                        print(f"{self._game_state = }")
                    else:
                        assert False
        elif mouse_click == models.MouseClick.DOWN and self._game_state == models.GameState.REMOVE and hover_coordinate is not None:
            self._game_board[hover_coordinate] = None
            self._player = self._player.switch()
            remaining = sum(player == self._player for _, player in self._game_board.items())
            if remaining < 3 and self._left_pieces[self._player] == 0:
                winner = self._player.switch()
            if self._left_pieces[self._player] > 0:
                self._game_state = models.GameState.PLACEMENT
                print(f"{self._game_state = }")
            elif self._left_pieces[self._player] == 0:
                self._game_state = models.GameState.SELECT
                print(f"{self._game_state = }")
            else:
                assert False


        if self._game_state == models.GameState.MOVEMENT:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
        elif hover_coordinate is not None:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)



        blacklist = set() if self._move_coordinate is None else { self._move_coordinate }
        game_board = assets.render_game_board_surface(self._game_board, highlighted_coordinates, blacklist=blacklist, scale=scale, is_delete=self._game_state==models.GameState.REMOVE)
        player = assets.player_surface[self._player]
        player_hover = assets.player_hover_surface[self._player]

        game_board_dest = width // 2, height // 2
        game_board_dest = utils.center_dest(game_board_dest, game_board.get_size())
        surface.blit(game_board, game_board_dest)

        player_hover_dest = pygame.mouse.get_pos()
        player_hover_dest = utils.center_dest(player_hover_dest, player_hover.get_size())
        if self._game_state == models.GameState.PLACEMENT or self._game_state == models.GameState.MOVEMENT or self._game_state == models.GameState.FLY:
            surface.blit(player_hover, player_hover_dest)

        font = assets.small_font

        rect = font.render_to(surface, (10, 10), "Spieler", (255, 255, 255))
        surface.blit(player, (10, rect.bottom))

        if winner is not None:
            return winner
        return None

    def __init__(self) -> None:
        self._move_coordinate: models.Coordinate | None = None
        self._game_state = models.GameState.PLACEMENT
        self._player: models.Player = models.Player.WHITE
        self._game_board: models.GameBoard = {
            Coordinate(ring, position): None
            for position in models.Position
            for ring in models.Ring
        }
        self._left_pieces: models.LeftPieces = { models.Player.WHITE: 5, models.Player.BLACK: 5 }


class EndScreen(models.Screen):
    def update(self, surface: pygame.Surface, events: t.Iterable[pygame.event.Event]) -> None:
        font = assets.small_font
        surf, rect = font.render(f"Spiel beendet: {self._winner}", (255, 255, 255))
        dest = utils.center_dest(surface.get_rect().center, rect.size)
        surface.blit(surf, dest)

    def __init__(self, winner: models.Player):
        self._winner = winner