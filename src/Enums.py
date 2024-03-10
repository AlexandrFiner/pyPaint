import enum


class ProjectionMode(enum.Enum):
    xy = 0,
    zy = 1,
    xz = 2


class TransitMode(enum.Enum):
    point1 = 0
    point2 = 1
    parallel = 2
    nothing = -1


class WorkingMode(enum.Enum):
    add_mode = 0
    edit_mode = 1