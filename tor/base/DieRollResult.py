
class DieRollResult:
    def __init__(self, found=False, result=-1, position=None):
        self.found = found
        self.result = result
        self.position = position

    def __str__(self):
        return "<DieRollResult: (found={}, result={}, position={})>".format(self.found, self.result, self.position)

    def __repr__(self):
        return self.__str__()