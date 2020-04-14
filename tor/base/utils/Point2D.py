import math

class Point2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return Point2D(dx, dy)

    def __str__(self):
        return "Point2D: x={} y={}".format(self.x, self.y)

    def __repr__(self):
        return "<Point2D: (x={}, y={})>".format(self.x, self.y)

    def length(self):
        return math.hypot(self.x, self.y)

    def distance(self, other):
        p = self - other
        return p.norm()