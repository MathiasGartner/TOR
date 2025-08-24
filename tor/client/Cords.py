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

    def __setitem__(self, i, data):
        self.lengths[i] = data

    def __getitem__(self, i):
        return self.lengths[i]

    def toPosition(self):
        print("WARNING: cord modification will not be used!")
        print("   Cords: {}".format(self))
        from tor.client.Position import Position #to avoid circular import - find better import strategy!
        x = cs.LX - round((cs.LX ** 2 + self.lengths[0] ** 2 - self.lengths[1] ** 2) / (2.0 * cs.LX))
        y = cs.LY - round((cs.LY ** 2 + self.lengths[0] ** 2 - self.lengths[3] ** 2) / (2.0 * cs.LY))
        z = math.sqrt(max(self.lengths[0] ** 2 - x ** 2 - y ** 2, 0))
        pos = Position(x, y, z)
        print("   Position: {}".format(pos))
        return pos

    def isValid(self):
        #TODO:
        return True