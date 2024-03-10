from json import JSONEncoder, JSONDecoder


class MyEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Line) or isinstance(obj, Point):
            return obj.__dict__()
        else:
            return JSONEncoder.default(self, obj)


def decode_object(obj):
    if 'p1' and 'p2' in obj:
        p1_dict = obj['p1']
        p2_dict = obj['p2']
        return Line(
            Point(
                p1_dict['x'],
                p1_dict['y'],
                p1_dict['z'],
                p1_dict['ok']
            ),
            Point(
                p2_dict['x'],
                p2_dict['y'],
                p2_dict['z'],
                p2_dict['ok']
            ),
            obj['color'],
            obj['width']
        )
    return obj


class Point:
    def __init__(self, x=None, y=None, z=None, ok=None):
        self.x = 0
        self.y = 0
        self.z = 0
        self.ok = 1
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if z is not None:
            self.z = z
        if ok is not None:
            self.ok = ok

    def __dict__(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "ok": self.ok
        }

    def __str__(self):
        return "x: {}, y: {}, z: {}, ok: {}".format(
            self.x, self.y, self.z, self.ok)


class Line:
    def __init__(self, p1=None, p2=None, color=None, width=None):
        self.p1 = Point()
        self.p2 = Point()
        self.color = "#000000"
        self.width = 1
        if p1 is not None:
            if isinstance(p1, Point):
                self.p1.x = p1.x
                self.p1.y = p1.y
                self.p1.z = p1.z
                self.p1.ok = p1.ok
        if p2 is not None:
            if isinstance(p2, Point):
                self.p2.x = p2.x
                self.p2.y = p2.y
                self.p2.z = p2.z
                self.p2.ok = p2.ok
        if color is not None:
            if isinstance(color, str):
                self.color = color
        if width is not None:
            if isinstance(width, int):
                self.width = width

    def get_directive_vector(self):
        return f"({self.p2.x - self.p1.x}, {self.p2.y - self.p1.y}, {self.p2.z - self.p1.z})"

    def __dict__(self):
        return {
            "p1": self.p1.__dict__(),
            "p2": self.p2.__dict__(),
            "color": self.color,
            "width": self.width
        }

    def __str__(self):
        return self.get_directive_vector()