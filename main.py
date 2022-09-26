import pygame

from utils import *

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("pyPaint")


def draw(win):
    win.fill(BG_COLOR)
    draw_lines()
    pygame.display.update()


def draw_lines():
    for i in range(len(points)):
        pygame.draw.line(WIN, BLACK, (points[i][0][0], points[i][0][1]), (points[i][1][0], points[i][1][1]))


def cursorOnLine(lineWidth=3):
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)


run = True
clock = pygame.time.Clock()
points = []
begin = False
posStart = None
posNow = None

while run:
    # Ограничение FPS
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    draw(WIN)

    # Нажата ЛЕВАЯ кнопка мыши
    if pygame.mouse.get_pressed()[0] and not begin:
        posStart = pygame.mouse.get_pos()
        begin = True

    # Нажата средняя кнопка мыши
    if pygame.mouse.get_pressed()[1]:
        pass

    if begin and posStart is not None:
        posNow = pygame.mouse.get_pos()
        pygame.draw.line(WIN, RED, (posStart[0], posStart[1]), (posNow[0], posNow[1]))

    if not pygame.mouse.get_pressed()[0] and begin and posNow is not None:
        points.append((posStart, posNow))
        begin = False

    if not begin:
        cursorOnLine()
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    pygame.display.flip()

pygame.quit()
