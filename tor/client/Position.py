class Position:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, other):
        return Position(self.x - other.x, self.y - other.y, self.z - other.z)