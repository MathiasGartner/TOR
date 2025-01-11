
import json

class DieRollResult:
    def __init__(self, found=False, result=-1, position=None):
        self.found = found
        self.result = result
        self.position = position

    def __str__(self):
        return f"<DieRollResult: (found={self.found}, result={self.result}, position={self.position})>"

    def __repr__(self):
        return self.__str__()