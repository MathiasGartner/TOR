class Cords:
    def __init__(self, lengths):
        self.lengths = lengths

    def __sub__(self, other):
        return Cords(self.lengths - other.lengths)

    def __str__(self):
        return "<Cords: (x={}, y={}, z={}, e={})>".format(self.lengths[0], self.lengths[1], self.lengths[2], self.lengths[3])

    def __repr__(self):
        return self.__str__()

    def isValid(self):
        #TODO
        return True