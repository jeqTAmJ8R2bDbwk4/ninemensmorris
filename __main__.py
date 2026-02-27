import typing as t

import pygame

import assets
import models
import states

FPS: t.Final[int] = 60


def main() -> None:
    pygame.init()
    running = True
    clock = pygame.time.Clock()
    surface = pygame.display.set_mode((640, 480), flags=pygame.RESIZABLE)
    game_board = {models.Coordinate(ring, position): None for position in models.Position for ring in models.Ring}
    left_pieces = {models.Player.WHITE: 3, models.Player.BLACK: 3}
    state = states.PlacementGameState(models.Player.WHITE, game_board, left_pieces)
    while running:
        resizing = False
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                resizing = True

        surface.fill((0, 0, 0))
        state = state.update(surface, events)

        if not resizing:
            clock.tick(FPS)
        else:
            pass  # Prevent screen from glitching

        pygame.display.flip()


if __name__ == '__main__':
    main()