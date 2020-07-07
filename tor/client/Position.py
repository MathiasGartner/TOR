import math

import tor.client.ClientSettings as cs

from tor.client.Cords import *

class Position:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Position(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, f):
        return Position(self.x * f, self.y * f, self.z * f)

    def __truediv__(self, f):
        return Position(self.x / f, self.y / f, self.z / f)

    def __str__(self):
        return "<Position: (x={}, y={}, z={})>".format(self.x, self.y, self.z)

    def __repr__(self):
        return self.__str__()

    def norm(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def toCordLengths(self):
        factor = 1.0
        diffs = cs.BOX_SIZE - self
        c1 = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2) * factor
        c2 = math.sqrt(diffs.x ** 2 + self.y ** 2 + self.z ** 2) * factor
        c3 = math.sqrt(diffs.x ** 2 + diffs.y ** 2 + self.z ** 2) * factor
        c4 = math.sqrt(self.x ** 2 + diffs.y ** 2 + self.z ** 2) * factor
        #return Cords([c1, c2, c3, c4])
        return Cords([c3, c2, c1, c4])

    def isValid(self):
        if self.x < 0 or self.y < 0 or self.z < 0:
            return False
        return True