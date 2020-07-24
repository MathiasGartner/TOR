import math

import tor.client.ClientSettings as cs

class Cords:
    def __init__(self, lengths):
        self.lengths = lengths

    def __sub__(self, other):
        return Cords(self.lengths - other.lengths)

    def __str__(self):
        return "<Cords: (x={}, y={}, z={}, e={})>".format(self.lengths[0], self.lengths[1], self.lengths[2], self.lengths[3])

    def __repr__(self):
        return self.__str__()

    def toPosition(self):
        from tor.client.Position import Position #to avoid circular import - find better import strategy!
        x = round((cs.LX ** 2 + self.lengths[2] ** 2 - self.lengths[1] ** 2) / (2.0 * cs.LX))
        y = round((cs.LY ** 2 + self.lengths[2] ** 2 - self.lengths[3] ** 2) / (2.0 * cs.LY))
        z = math.sqrt(max(self.lengths[2] ** 2 - x ** 2 - y ** 2, 0))
        return Position(x, y, z)

    def isValid(self):
        #TODO
        return True