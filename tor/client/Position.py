import math

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

    def __setitem__(self, coordinate, data):
        if coordinate == 0:
            self.x = data
        elif coordinate == 1:
            self.y = data
        elif coordinate == 2:
            self.z = data
        else:
            raise Exception("only x, y an z (0, 1, 2) are available.")

    def __getitem__(self, coordinate):
        if coordinate == 0:
            return self.x
        elif coordinate == 1:
            return self.y
        elif coordinate == 2:
            return self.z
        else:
            raise Exception("only x, y an z (0, 1, 2) are available.")

    def norm(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def toCordLengths(self):
        import tor.client.ClientSettings as cs
        from tor.client.Cords import Cords
        diffs = cs.BOX_SIZE - self
        c1 = math.sqrt(diffs.x ** 2 + diffs.y ** 2 + self.z ** 2) * cs.CORD_FACTOR_X
        c2 = math.sqrt(diffs.x ** 2 + self.y ** 2 + self.z ** 2) * cs.CORD_FACTOR_Y
        c3 = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2) * cs.CORD_FACTOR_Z
        c4 = math.sqrt(self.x ** 2 + diffs.y ** 2 + self.z ** 2) * cs.CORD_FACTOR_E
        return Cords([c1, c2, c3, c4])

    def isValid(self):
        import tor.client.ClientSettings as cs
        if self.x < 0 or self.y < 0 or self.z < 0:
            return False
        if self.x > cs.LX or self.y>cs.LY or self.z>cs.LZ:
            return False
        return True