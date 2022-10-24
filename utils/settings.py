import pygame

pygame.init()
pygame.font.init()

# Действия
ACTION_NO = 0
ACTION_DRAW = 1
ACTION_MOVE_POINT = 2
ACTION_MOVE_LINE = 3
ACTION_MOVE_GROUP = 4
ACTION_MAKE_GROUP = 5

# Размер окна
WIDTH, HEIGHT = 600, 700

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Частота кадров
FPS = 120

# Размер панели с кнопками
TOOLBAR_HEIGHT = HEIGHT - WIDTH

# Цвет фона
BG_COLOR = WHITE


def get_font(size):
    return pygame.font.SysFont("comicsans", size)
