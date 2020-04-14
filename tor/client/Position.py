import math

import tor.client.ClientSettings as cs

from tor.client.Cords import Cords

class Position:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, other):
        return Position(self.x - other.x, self.y - other.y, self.z - other.z)

    def toCordLengths(self):
        diffs = cs.BOX_SIZE - self
        c1 = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
        c2 = math.sqrt(diffs.x ** 2 + self.y ** 2 + self.z ** 2)
        c3 = math.sqrt(diffs.x ** 2 + diffs.y ** 2 + self.z ** 2)
        c4 = math.sqrt(self.x ** 2 + diffs.y ** 2 + self.z ** 2)
        return Cords([c1, c2, c3, c4])