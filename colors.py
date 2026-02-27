import pygame

import typing as t

import models


BOARD_LINE_COLOR: t.Final[models.Color] = pygame.color.THECOLORS['grey20']
BOARD_BACKGROUND_COLOR: t.Final[models.Color] = pygame.color.THECOLORS['grey85']
BOARD_DOT_COLOR: t.Final[models.Color] = pygame.color.THECOLORS['grey20']
BOARD_DOT_BORDER_COLOR: t.Final[models.Color] = pygame.color.THECOLORS['grey75']

PIECE_WHITE: t.Final[models.Color] = pygame.color.THECOLORS['grey90']
PIECE_BLACK: t.Final[models.Color] = pygame.color.THECOLORS['grey10']

PIECE_BLACK_BORDER: t.Final[models.Color] = pygame.color.THECOLORS['grey20']
PIECE_WHITE_BORDER: t.Final[models.Color] = pygame.color.THECOLORS['grey80']

HIGHLIGHT: t.Final[models.Color] = (*pygame.color.THECOLORS['red'][:3], 128)