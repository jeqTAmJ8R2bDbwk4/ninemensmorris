import typing as t

import pygame
import pygame.freetype

import assets
import models
import screens

FPS: t.Final[int] = 60


def main() -> None:
    pygame.init()
    pygame.freetype.init()
    running = True
    clock = pygame.time.Clock()
    surface = pygame.display.set_mode((640, 480), flags=pygame.RESIZABLE)
    screen: models.Screen = screens.GameScreen()
    assets.set_scale(min(surface.get_size()))
    while running:
        resizing = False
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                assets.set_scale(min(surface.get_size()))
                resizing = True

        surface.fill((0, 0, 0))
        out = screen.update(surface, events)
        if isinstance(screen, screens.GameScreen):
            if out is not None:
                screen = screens.EndScreen(out)

        if not resizing:
            clock.tick(FPS)
        else:
            pass  # Prevent screen from glitching

        pygame.display.flip()


if __name__ == '__main__':
    main()