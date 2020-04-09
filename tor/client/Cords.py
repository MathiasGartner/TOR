class Cords:
    def __init__(self, lengths):
        self.lengths = lengths

    def __sub__(self, other):
        return Cords(self.lengths - other.lengths)

    def isValid(self):
        #TODO
        return True