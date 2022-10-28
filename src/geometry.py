import math
import numpy as np


class Geometry:
    def __init__(self):
        self._angle_x = 0
        self._angle_y = 0
        self._angle_z = 0
        self._zoom = 0.5

    def _reset_rotation(self):
        self._angle_x = self._angle_y = self._angle_z = 0

    def transform_point(self, point, rotation_x, rotation_y, rotation_z):
        print(point)
        rotated_2d = np.matmul(rotation_x, point)
        rotated_2d = np.matmul(rotation_y, rotated_2d)
        rotated_2d = np.matmul(rotation_z, rotated_2d)

        print(rotated_2d)
        # z = 0.5 / (self._zoom - rotated_2d[2][0])
        z = 1
        projection_matrix = [[z, 0, 0],
                             [0, z, 0]]
        print(projection_matrix)
        projected_2d = np.matmul(projection_matrix, rotated_2d)

        x = int(projected_2d[0][0])
        y = int(projected_2d[1][0])

        print(projected_2d)

        return x, y

    def calculate_rot_matrix(self):
        rotation_x = [[1, 0, 0],
                      [0, math.cos(self._angle_x), -math.sin(self._angle_x)],
                      [0, math.sin(self._angle_x), math.cos(self._angle_x)]]

        rotation_y = [[math.cos(self._angle_y), 0, -math.sin(self._angle_y)],
                      [0, 1, 0],
                      [math.sin(self._angle_y), 0, math.cos(self._angle_y)]]

        rotation_z = [[math.cos(self._angle_z), -math.sin(self._angle_z), 0],
                      [math.sin(self._angle_z), math.cos(self._angle_z), 0],
                      [0, 0, 1]]

        return rotation_x, rotation_y, rotation_z
