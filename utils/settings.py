import pygame

pygame.init()
pygame.font.init()

# Размер окна
WIDTH, HEIGHT = 600, 700

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Частота кадров
FPS = 60

# Размер панели с кнопками
TOOLBAR_HEIGHT = HEIGHT - WIDTH

# Цвет фона
BG_COLOR = WHITE


def get_font(size):
    return pygame.font.SysFont("comicsans", size)
