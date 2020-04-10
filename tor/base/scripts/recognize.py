
from tor.base.DiceRecognizer import  DiceRecognizer

dr = DiceRecognizer()
im = dr.readDummyImage()
dr.getDiePosition(im, withUI=True)

