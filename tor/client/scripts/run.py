#!/usr/bin/env python3

import random
import sys
import time

import tor.client.ClientSettings as cs
from tor.client.LedManager import LedManager
from tor.client.MovementManager import MovementManager
from tor.client.Position import Position

try:
    mm = MovementManager()

    mm.initBoard()
    time.sleep(0.5)
except:
    mm = None
    print("ERROR: could not connect to SKR board.")


mode = 4
if len(sys.argv) > 1:
    mode=int(sys.argv[1])
print("mode: ", mode)

if mode == 0:
    diePosition = Position(100, 30, 210)
    mm.moveToPos(cs.HOME_POSITION)
    mm.moveToPos(diePosition)
    mm.moveToPos(cs.HOME_POSITION)

    dieX = 120
    dieY = 160
    mm.moveToXYPosDie(dieX, dieY)
    mm.waitForMovementFinished(0.5)
    mm.moveToXPosRamp(dieX)

elif mode == 1: #move to x y and pick up die
    dieX = int(sys.argv[2])
    dieY = int(sys.argv[3])
    mm.moveToXYPosDie(dieX, dieY)
    mm.waitForMovementFinished(0.5)
    mm.moveToXPosRamp(dieX)

elif mode == 2: #move to x y z
    pos = Position(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    mm.moveToPos(pos)

elif mode == 3: #move to all corners
    mm.moveToAllCorners()

elif mode == 4: #search for die
    mm.searchForDie()
    mm.moveToXPosRamp(cs.LX/2)

elif mode == 5: #move to x y z segmented
    pos = Position(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    mm.moveToPosSegmented(pos)

elif mode == 6: #home to Z anchor
    mm.doHoming()

elif mode == 7: #test dropoff
    while (True):
        mm.doHoming()
        mm.waitForMovementFinished(0.5)
        mm.moveToPos(cs.CENTER_TOP)
        mm.waitForMovementFinished(0.5)
        mm.moveToPos(cs.DROPOFF_ADVANCE_POSITION)
        mm.waitForMovementFinished(0.5)
        mm.moveToPos(cs.DROPOFF_POSITION, segmented=True)
        mm.waitForMovementFinished(2)
        mm.moveToPos(cs.DROPOFF_ADVANCE_POSITION)
        mm.waitForMovementFinished(0.5)

elif mode == 8:  # led test
    lm = LedManager()
    lm.test()
    for i in range(1, 7):
        lm.showResult(i)
        time.sleep(1)
    for i in [random.randint(1, 6) for x in range(1, 4)]:
        lm.showResult(i)
        time.sleep(1)
    lm.clear()

elif mode == 9: # take picture and search dice dots
    from tor.base.DieRecognizer import DieRecognizer
    if cs.ON_RASPI:
        from tor.client.Camera import Camera
    #lm = LedManager()
    dr = DieRecognizer()
    if cs.ON_RASPI:
        cam = Camera()
        image = cam.takePicture()
    else:
        image = dr.readDummyImage()
    print("analyze picture...")
    found, diePosition, result, processedImages = dr.getDiePosition(image, returnOriginalImg=True)
    print("write image...")
    dr.writeImage(processedImages[1])
    print("result:", result)
    #lm.showResult(result)

if mm is not None:
    mm.waitForMovementFinished(2)
    #mm.moveHome()


