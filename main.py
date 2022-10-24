import math
import numpy

from utils import *

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("pyPaint")


def draw(win, cursorPoint):
    win.fill(BG_COLOR)
    draw_lines()

    if currentAction == ACTION_DRAW:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    elif currentAction == ACTION_MOVE_POINT:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    elif currentAction == ACTION_NO:
        if cursorOnLineEnd(cursor, radius=5) is not None:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
        elif cursorOnLine(cursorPoint, zoneRadius=5) is not None:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    pygame.display.update()


def draw_lines():
    for i in range(len(points)):
        if pointId is not None:
            if currentAction == ACTION_MOVE_POINT and i == pointId[0]:
                continue

            if currentAction == ACTION_MOVE_LINE and i == pointId:
                continue

        if currentAction == ACTION_MOVE_GROUP and i in linesInGroup:
            continue

        x1 = points[i][0][0]
        x2 = points[i][1][0]
        y1 = points[i][0][1]
        y2 = points[i][1][1]

        A = x2 - x1
        B = y2 - y1
        C = x1 * y2 - x2 * y1

        B *= -1

        font = get_font(22)
        text_surface = font.render(f"{A}x + {B}y + {C}", 1, BLACK)
        centerLine = (
            ((x1 + x2) / 2),
            ((y1 + y2) / 2),
        )
        WIN.blit(text_surface, centerLine)
        if i in linesInGroup:
            pygame.draw.line(WIN, BLUE, (x1, y1), (x2, y2))
        else:
            pygame.draw.line(WIN, BLACK, (x1, y1), (x2, y2))


def cursorOnLine(cursorPoint, zoneRadius=3):
    # credits: https://clck.ru/R9STG
    # def dist(x1_, x2_, y1_, y2_):
    #     return math.sqrt((x2_ - x1_) ** 2 + (y2_ - y1_) ** 2)
    #
    # def dot(x1_, x2_, y1_, y2_):
    #     return (x1_ * x2_) + (y1_ * y2_)
    #
    # def vector(x1_, x2_, y1_, y2_):
    #     distance = [x1 - x2, y1 - y2]
    #     norm = math.sqrt(distance[0] ** 2 + distance[1] ** 2)
    #     direction = [distance[0] / norm, distance[1] / norm]
    #     return direction

    for i in range(len(points)):
        x1 = points[i][0][0]
        x2 = points[i][1][0]
        y1 = points[i][0][1]
        y2 = points[i][1][1]

        x = cursorPoint[0]
        y = cursorPoint[1]

        yTop = max(y1, y2)
        yBottom = min(y1, y2)

        yTop += 20
        yBottom -= 20

        if y < yBottom or y > yTop:
            continue

        # (x - x1)/(x2 - x1) = (y - y1)/(y2 - y1)
        xCord = ((y - y1)*(x2 - x1))/(y2 - y1) + x1
        distToLine = abs(x - xCord)
        if distToLine > zoneRadius:
            continue

        return i

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
linesInGroup = []
currentAction = ACTION_NO
posStart = None
pointId = None
positionMovePoint = None
hoverLineId = None

while run:
    # Ограничение FPS
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    cursor = pygame.mouse.get_pos()
    draw(WIN, cursor)

    # Нажата ЛЕВАЯ кнопка мыши

    if currentAction == ACTION_NO:
        lineId = cursorOnLine(cursor, zoneRadius=5)
        # if lineId is not None:
        hoverLineId = lineId

    if pygame.mouse.get_pressed()[0] and pygame.key.get_pressed()[pygame.K_LCTRL]:
        if currentAction == ACTION_NO or ACTION_MAKE_GROUP:
            if hoverLineId is not None and hoverLineId not in linesInGroup:
                currentAction = ACTION_MAKE_GROUP
                linesInGroup.append(hoverLineId)

    if pygame.mouse.get_pressed()[0]:
        # ЛКМ ЗАЖАТА
        if currentAction == ACTION_NO:
            pointId = cursorOnLineEnd(cursor, radius=5)
            if pointId is not None:
                currentAction = ACTION_MOVE_POINT
            else:
                posStart = cursor
                if hoverLineId is not None:
                    if not linesInGroup:
                        pointId = hoverLineId
                        currentAction = ACTION_MOVE_LINE
                    else:
                        currentAction = ACTION_MOVE_GROUP
                else:
                    linesInGroup = []
                    currentAction = ACTION_DRAW

                print(currentAction, linesInGroup)


    # Нажата средняя кнопка мыши
    if pygame.mouse.get_pressed()[2]:
        # ПКМ
        if currentAction == ACTION_NO:
            # Удаление
            if hoverLineId is not None:
                points.pop(hoverLineId)
                if hoverLineId in linesInGroup:
                    linesInGroup.remove(hoverLineId)
                # print('Удаление')

    if not pygame.mouse.get_pressed()[0]:
        if currentAction == ACTION_DRAW:
            # Это не точка!
            if posStart != cursor:
                points.append((posStart, cursor))

        if currentAction == ACTION_MOVE_POINT:
            if positionMovePoint is not None and pointId is not None:
                points[pointId[0]] = positionMovePoint

        if currentAction == ACTION_MOVE_LINE:
            if hoverLineId is not None:
                moved = (cursor[0]-posStart[0], cursor[1]-posStart[1])
                points[hoverLineId] = positionMovePoint

        if currentAction == ACTION_MOVE_GROUP:
            if linesInGroup:
                moved = (cursor[0] - posStart[0], cursor[1] - posStart[1])
                for lineGroupId in linesInGroup:
                    print('move group', points[lineGroupId])
                    positionMovePoint = (
                        (points[lineGroupId][0][0] + moved[0], points[lineGroupId][0][1] + moved[1]),
                        (points[lineGroupId][1][0] + moved[0], points[lineGroupId][1][1] + moved[1]),
                    )
                    points[lineGroupId] = positionMovePoint
                    print('move group', points[lineGroupId])

        currentAction = ACTION_NO

    if currentAction == ACTION_DRAW and posStart is not None:
        pygame.draw.line(WIN, RED, (posStart[0], posStart[1]), (cursor[0], cursor[1]))

    if currentAction == ACTION_MOVE_GROUP and posStart is not None and linesInGroup is not []:
        moved = (cursor[0]-posStart[0], cursor[1]-posStart[1])
        for lineGroupId in linesInGroup:
            positionMovePoint = (
                (points[lineGroupId][0][0] + moved[0], points[lineGroupId][0][1] + moved[1]),
                (points[lineGroupId][1][0] + moved[0], points[lineGroupId][1][1] + moved[1]),
            )
            pygame.draw.line(WIN, RED, positionMovePoint[0], positionMovePoint[1])

    if currentAction == ACTION_MOVE_LINE and hoverLineId is not None and posStart is not None:
        moved = (cursor[0]-posStart[0], cursor[1]-posStart[1])

        positionMovePoint = (
            (points[hoverLineId][0][0] + moved[0], points[hoverLineId][0][1] + moved[1]),
            (points[hoverLineId][1][0] + moved[0], points[hoverLineId][1][1] + moved[1]),
        )
        pygame.draw.line(WIN, RED, positionMovePoint[0], positionMovePoint[1])

    if currentAction == ACTION_MOVE_POINT and pointId is not None:
        positionMovePoint = (
            (points[pointId[0]][0][0], points[pointId[0]][0][1]), (cursor[0], cursor[1]),
        ) if pointId[1] == 1 else (
            (points[pointId[0]][1][0], points[pointId[0]][1][1]), (cursor[0], cursor[1]),
        )
        pygame.draw.line(WIN, RED, positionMovePoint[0], positionMovePoint[1])

    pygame.display.flip()

pygame.quit()
