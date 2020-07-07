import sys
#sys.path.append("C:\\Users\\David\\Documents\\TOR")

import argparse
import time

from tor.client import ClientSettings as cs
from tor.client.MovementManager import MovementManager
from tor.client.Position import Position




parser = argparse.ArgumentParser()
parser.add_argument("position", nargs='*', default=[cs.CENTER_TOP.x, cs.CENTER_TOP.y, cs.CENTER_TOP.z], type=float)
parser.add_argument("-f", dest="feedratePercentage", default=cs.FEEDRATE_PERCENTAGE, type=int)
parser.add_argument("-c", dest="doHoming", action="store_true")
parser.add_argument("-ce", dest="doHomingexact", action="store_true")
parser.add_argument("-s", dest="segmented", action="store_true")
parser.add_argument("-start", dest='start', action="store_true")
parser.add_argument("-find", dest='find', action="store_true")
args = parser.parse_args()

mm = MovementManager()
mm.initBoard()
time.sleep(0.5)

if args.feedratePercentage != cs.FEEDRATE_PERCENTAGE:
    mm.setFeedratePercentage(args.feedratePercentage)

if args.doHoming:
    mm.doHoming()
    exit(0)

#args.start=True

if args.doHomingexact:
    mm.moveToPos(Position(120,120,120), args.segmented)
    mm.doHoming()
    mm.waitForMovementFinished()
    mm.moveToPos(Position(120, 120, 100), args.segmented)
    mm.waitForMovementFinished()
    mm.doHoming()
    mm.moveToPos(Position(120, 120, 100), args.segmented)
    exit(0)



if args.start:
    cur_po=mm.getCurrentPosition()
    mm.moveToPos(Position(cur_po.x, cur_po.y, 50), args.segmented)
    mm.waitForMovementFinished()
    mm.moveToPos(Position(125,50,30), args.segmented)
    mm.waitForMovementFinished()
    mm.setFeedratePercentage(50)
    mm.moveToPos(Position(125, 15, 10), args.segmented)
    mm.waitForMovementFinished()
    mm.moveToPos(Position(130, 4, 10), args.segmented)
    mm.waitForMovementFinished()
    mm.setFeedratePercentage(250)
    time.sleep(2)
    mm.rollDie()
    if (args.find):
        time.sleep(3)
        from tor.base.DieRecognizer import DieRecognizer
        from tor.client.Camera import Camera
        dr=DieRecognizer()
        cam = Camera()
        mm.setLed(200)
        image = cam.takePicture()
        time.sleep(1)
        mm.setLed(0)
        found, diePosition, result, processedImages = dr.getDiePosition(image, returnOriginalImg=True)
        #dr.writeImage(processedImages[1])
        print(result)
        if (found):
            print(diePosition)
            mm.moveToPos(Position(min(diePosition.x*1.1,241),diePosition.y,50), args.segmented)
            mm.waitForMovementFinished()
            mm.moveToPos(Position(min(diePosition.x*1.1,241), diePosition.y, 205), args.segmented)
        else:
            print('Die not found')
    exit(0)


pos = Position(args.position[0], args.position[1], args.position[2])
if pos.isValid():
    mm.moveToPos(pos,args.segmented)
