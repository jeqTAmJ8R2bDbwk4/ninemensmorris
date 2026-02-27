import time

import pygame
import pygame.freetype

import typing as t
import pathlib


import board
import constants
import type

FPS = 120
ROOT_PATH = pathlib.Path(__file__).parent
ASSETS_PATH = ROOT_PATH / 'assets'
TEMPLATE_PATH = ASSETS_PATH / 'template.png'

COLOR_BLACK = pygame.color.THECOLORS['black']

BOARD_LINES = [
    (( 20/300,  20/300), (280/300,  20/300)),
    ((280/300,  20/300), (280/300, 280/300)),
    ((280/300, 280/300), (20/300,  280/300)),
    (( 20/300,  280/300), ( 20/300,  20/300))
]

global_running = True



def draw_move(surface: pygame.Surface, player: type.Player, b: type.GameBoard) -> None:
    global global_running

    rects = {}
    running = True
    draw_clock = pygame.time.Clock()
    original_coord = None
    while running and global_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                global_running = False
            if event.type == pygame.KEYDOWN:
                pass
            if event.type == pygame.MOUSEBUTTONDOWN and original_coord is None:
                mouse_pos = pygame.mouse.get_pos()
                #print(f"{mouse_pos = }")
                for coord, rect in rects.items():
                    # print(f"{rect = }")
                    if rect.collidepoint(mouse_pos):
                        # print("Hey")
                        original_coord = coord
                        del b[coord]
                        print("down")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    running = False
                    continue
                if event.key == pygame.K_p:
                    player = type.Player.BLACK if player == type.Player.WHITE else type.Player.WHITE
                    continue
            if event.type == pygame.MOUSEBUTTONUP and original_coord is not None:
                mouse_pos = pygame.mouse.get_pos()
                # print(f"{mouse_pos = }")
                for coord, rect in rects.items():
                    # print(f"{rect = }")
                    if rect.collidepoint(mouse_pos):
                        # print("Hey")
                        print(coord)
                        b[coord] = player
                        original_coord = None

                        print("up")
                        break
                else:
                    b[original_coord] = player
                    original_coord = None

        print(b)
        surface.fill(COLOR_BLACK)
        update_board(surface, b)

        surface_width, surface_height = surface.get_size()
        size = get_size(surface)
        image_margin_left_template = (surface_width - size) // 2
        image_margin_top_template = (surface_height - size) // 2
        # print(f"{image_margin_left_template = }, {image_margin_top_template =}")

        rects.clear()
        num_of_player = sum(1 for bi in b.values() if bi == player)
        if original_coord is not None:
            num_of_player += 1


        print("num_of_player", num_of_player)
        for ring in type.Ring:
            for pos in type.Position:
                coord = type.Coordinate(ring, pos)
                p = b.get(coord, None)
                if original_coord is None:
                    if p is None: #Test or p == player:
                        continue
                else:
                    if coord == original_coord:
                        continue
                    if p is not None:
                        continue
                    if num_of_player > 3 and coord not in constants.BOARD_EDGES[original_coord]:
                        continue


                highlight_surface = board.draw_highlight(size, time.time())
                x, y = constants.COORD_WORLD_POS[coord]
                x, y = board.to_abs((x, y), size)
                x += image_margin_left_template
                y += image_margin_top_template
                x -= highlight_surface.get_size()[0] // 2
                y -= highlight_surface.get_size()[1] // 2
                # print(x, y, size)
                surface.blit(highlight_surface, (x, y))
                rects[coord] = pygame.Rect(x, y, highlight_surface.get_width(), highlight_surface.get_height())

        if original_coord is None:
            mouse_pos = pygame.mouse.get_pos()
            for _, rect in rects.items():
                if rect.collidepoint(mouse_pos):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    break
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)

        if original_coord is not None:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player_surface = board.draw_player(player, size)
            rect = player_surface.get_rect()
            x, y = rect.size
            surface.blit(player_surface, (mouse_x - x // 2, mouse_y - y // 2))

        pygame.display.flip()
        draw_clock.tick(FPS)


def draw_delete(surface: pygame.Surface, player: type.Player, b: type.GameBoard) -> None:
    global global_running

    rects = {}
    running = True
    draw_clock = pygame.time.Clock()
    while running and global_running:
        # Test
        # print(len(b))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                global_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    running = False
                    continue
                if event.key == pygame.K_p:
                    player = type.Player.BLACK if player == type.Player.WHITE else type.Player.WHITE
                    continue
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()
                # print(f"{mouse_pos = }")
                for coord, rect in rects.items():
                    # print(f"{rect = }")
                    if rect.collidepoint(mouse_pos):
                        # print("Hey")
                        del b[coord]

        mouse_pos = pygame.mouse.get_pos()

        for _, rect in rects.items():
            if rect.collidepoint(mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                break
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        surface.fill(COLOR_BLACK)
        update_board(surface, b)

        surface_width, surface_height = surface.get_size()
        size = get_size(surface)
        image_margin_left_template = (surface_width - size) // 2
        image_margin_top_template = (surface_height - size) // 2
        # print(f"{image_margin_left_template = }, {image_margin_top_template =}")

        rects.clear()
        for ring in type.Ring:
            for pos in type.Position:
                coord = type.Coordinate(ring, pos)
                print(b)
                p = b.get(coord, None)
                if p is None:
                    continue
                if p == player:
                    continue
                highlight_surface = board.draw_highlight(size, time.time())
                x, y = constants.COORD_WORLD_POS[coord]
                x, y = board.to_abs((x, y), size)
                x += image_margin_left_template
                y += image_margin_top_template
                x -= highlight_surface.get_size()[0] // 2
                y -= highlight_surface.get_size()[1] // 2
                # print(x, y, size)
                surface.blit(highlight_surface, (x, y))
                rects[coord] = pygame.Rect(x, y, highlight_surface.get_width(), highlight_surface.get_height())

        pygame.display.flip()
        draw_clock.tick(FPS)


def draw_hover(surface: pygame.Surface, player: type.Player, b: type.GameBoard) -> None:
    global global_running

    rects = {}
    running = True
    draw_clock = pygame.time.Clock()
    while running and global_running:
        # Test
        # print(len(b))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                global_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    running = False
                    continue
                if event.key == pygame.K_p:
                    player = type.Player.BLACK if player == type.Player.WHITE else type.Player.WHITE
                    continue
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()
                # print(f"{mouse_pos = }")
                for coord, rect in rects.items():
                    # print(f"{rect = }")
                    if rect.collidepoint(mouse_pos):
                        # print("Hey")
                        b[coord] = player

        mouse_pos = pygame.mouse.get_pos()

        for _, rect in rects.items():
            if rect.collidepoint(mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                break
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        surface.fill(COLOR_BLACK)
        update_board(surface, b)

        surface_width, surface_height = surface.get_size()
        size = get_size(surface)
        image_margin_left_template = (surface_width - size) // 2
        image_margin_top_template = (surface_height - size) // 2
        # print(f"{image_margin_left_template = }, {image_margin_top_template =}")

        rects.clear()
        for ring in type.Ring:
            for pos in type.Position:
                coord = type.Coordinate(ring, pos)
                print(b)
                if coord in b:
                    continue
                highlight_surface = board.draw_highlight(size, time.time())
                x, y = constants.COORD_WORLD_POS[coord]
                x, y = board.to_abs((x, y), size)
                x += image_margin_left_template
                y += image_margin_top_template
                x -= highlight_surface.get_size()[0] // 2
                y -= highlight_surface.get_size()[1] // 2
                # print(x, y, size)
                surface.blit(highlight_surface, (x, y))
                rects[coord] = pygame.Rect(x, y, highlight_surface.get_width(), highlight_surface.get_height())

        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_surface = board.draw_player(player, size)
        rect = player_surface.get_rect()
        x, y = rect.size
        surface.blit(player_surface, (mouse_x - x // 2, mouse_y - y // 2))

        pygame.display.flip()
        draw_clock.tick(FPS)


def get_size(surface: pygame.Surface) -> int:
    surface_width, surface_height = surface.get_size()
    return min(surface_width, surface_height)


def update_board(surface: pygame.Surface, b: type.GameBoard) -> None:
    surface_width, surface_height = surface.get_size()
    size = get_size(surface)
    image_margin_left_template = (surface_width - size) // 2
    image_margin_top_template = (surface_height - size) // 2
    board_surface = board.draw_board_surface(b, size)
    surface.blit(board_surface, (image_margin_left_template, image_margin_top_template))




def main() -> None:
    surface_width = 800
    surface_height = 600

    pygame.init()

    surface = pygame.display.set_mode((surface_width, surface_height), pygame.RESIZABLE)
    pygame.display.set_caption("Snake")
    b = {}

    while global_running:
        draw_hover(surface, type.Player.WHITE, b)
        draw_move(surface, type.Player.WHITE, b)
        draw_delete(surface, type.Player.WHITE, b)


if __name__ == '__main__':
    main()