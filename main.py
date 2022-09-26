import math

from utils import *

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("pyPaint")


def draw(win, cursorPoint):
    win.fill(BG_COLOR)
    draw_lines()

    if currentAction == ACTION_NO:
        if cursorOnLineEnd(cursorPoint, radius=5) is not None:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    if currentAction == ACTION_DRAW:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    if currentAction == ACTION_MOVE_POINT:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    pygame.display.update()


def draw_lines():
    for i in range(len(points)):
        if pointId is not None:
            if currentAction == ACTION_MOVE_POINT and i == pointId[0]:
                continue

        A = points[i][0][1] + points[i][1][1]
        B = points[i][1][0] + points[i][0][0]
        C = points[i][0][0] * points[i][1][1] + points[i][1][0]*points[i][0][1]

        font = get_font(22)
        text_surface = font.render(f"{A}x + {B}y + {C}", 1, BLACK)
        centerLine = (
            ((points[i][0][0] + points[i][1][0]) / 2),
            ((points[i][0][1] + points[i][1][1]) / 2),
        )
        WIN.blit(text_surface, centerLine)
        pygame.draw.line(WIN, BLACK, (points[i][0][0], points[i][0][1]), (points[i][1][0], points[i][1][1]))


def cursorOnLine(cursorPoint, lineWidth=3):
    for i in range(len(points)):
        result = (
                (cursorPoint[1] - points[i][0][1]) * (points[i][1][0] - points[i][0][0]) -
                (cursorPoint[0] - points[i][0][0]) * (points[i][1][1] - points[i][0][1])
        )

        return None

    return None


def cursorOnLineEnd(cursorPoint, radius=5):
    for i in range(len(points)):
        if (pow((cursorPoint[0] - points[i][0][0]), 2) + pow((cursorPoint[1] - points[i][0][1]), 2)) <= pow(radius, 2):
            return i, 0

        if (pow((cursorPoint[0] - points[i][1][0]), 2) + pow((cursorPoint[1] - points[i][1][1]), 2)) <= pow(radius, 2):
            return i, 1

    return None


run = True
clock = pygame.time.Clock()
points = []
currentAction = ACTION_NO
posStart = None
pointId = None
positionMovePoint = None

while run:
    # Ограничение FPS
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    cursor = pygame.mouse.get_pos()
    draw(WIN, cursor)

    # Нажата ЛЕВАЯ кнопка мыши
    if pygame.mouse.get_pressed()[0]:
        if currentAction == ACTION_NO:
            pointId = cursorOnLineEnd(cursor, radius=5)
            if pointId is not None:
                currentAction = ACTION_MOVE_POINT
            else:
                lineId = cursorOnLine(cursor, lineWidth=3)
                if lineId is not None:
                    pass
                else:
                    posStart = cursor
                    currentAction = ACTION_DRAW


    if not pygame.mouse.get_pressed()[0]:
        if currentAction == ACTION_DRAW:
            points.append((posStart, cursor))

        if currentAction == ACTION_MOVE_POINT:
            if positionMovePoint is not None and pointId is not None:
                points[pointId[0]] = positionMovePoint

        currentAction = ACTION_NO

    # Нажата средняя кнопка мыши
    if pygame.mouse.get_pressed()[1]:
        pass

    if currentAction == ACTION_DRAW and posStart is not None:
        pygame.draw.line(WIN, RED, (posStart[0], posStart[1]), (cursor[0], cursor[1]))

    if currentAction == ACTION_MOVE_POINT and pointId is not None:
        positionMovePoint = (
            (points[pointId[0]][0][0], points[pointId[0]][0][1]), (cursor[0], cursor[1]),
        ) if pointId[1] == 1 else (
            (points[pointId[0]][1][0], points[pointId[0]][1][1]), (cursor[0], cursor[1]),
        )
        pygame.draw.line(WIN, RED, positionMovePoint[0], positionMovePoint[1])

    pygame.display.flip()

pygame.quit()
