import math
import numpy as np


class Geometry:
    def __init__(self, canvas_width, canvas_height):
        self._angle_x = 0
        self._angle_y = 0
        self._angle_z = 0
        self._zoom = 1
        self.CANVAS_WIDTH = canvas_width
        self.CANVAS_HEIGHT = canvas_height
        self.OBJECT_POSITION = [canvas_width // 2, canvas_height // 2 - 20]

    def _reset_rotation(self):
        self._angle_x = self._angle_y = self._angle_z = 0
        self._zoom = 1

    def transform_point(self, point, rotation_x, rotation_y, rotation_z):
        point[0][0] -= self.OBJECT_POSITION[0]
        point[1][0] -= self.OBJECT_POSITION[1]
        rotated_2d = np.matmul(rotation_x, point)
        rotated_2d = np.matmul(rotation_y, rotated_2d)
        rotated_2d = np.matmul(rotation_z, rotated_2d)

        # z = 0.5 / (self._zoom - rotated_2d[2][0])
        z = self._zoom
        projection_matrix = [[z, 0, 0],
                             [0, z, 0]]

        projected_2d = np.matmul(projection_matrix, rotated_2d)

        x = int(projected_2d[0][0]) + self.OBJECT_POSITION[0]
        y = int(projected_2d[1][0]) + self.OBJECT_POSITION[1]

        # x = int(projected_2d[0][0])
        # y = int(projected_2d[1][0])

        return x, y

    def get_original_point(self, point, rotation_x, rotation_y, rotation_z):
        pass

    def calculate_rot_matrix(self, angle_x, angle_y, angle_z):
        rotation_x = [[1, 0, 0],
                      [0, math.cos(angle_x), -math.sin(angle_x)],
                      [0, math.sin(angle_x), math.cos(angle_x)]]

        rotation_y = [[math.cos(angle_y), 0, -math.sin(angle_y)],
                      [0, 1, 0],
                      [math.sin(angle_y), 0, math.cos(angle_y)]]

        rotation_z = [[math.cos(angle_z), -math.sin(angle_z), 0],
                      [math.sin(angle_z), math.cos(angle_z), 0],
                      [0, 0, 1]]

        return rotation_x, rotation_y, rotation_z
