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
        return f"<Point2D: (x={self.x:.2f}, y={self.y:.2f})>"

    def __repr__(self):
        return self.__str__()

    def length(self):
        return math.hypot(self.x, self.y)

    def distance(self, other):
        p = self - other
        return p.norm()