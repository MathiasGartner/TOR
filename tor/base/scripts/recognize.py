
from tor.base.DiceRecognizer import  DiceRecognizer

dr = DiceRecognizer()
im = dr.readDummyImage()
result = dr.getDiePosition(im, withUI=True)
print(result)
