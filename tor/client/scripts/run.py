#!/usr/bin/env python3

import sys
import time

import tor.client.ClientSettings as cs
from tor.client.MovementManager import MovementManager
from tor.client.Position import Position

mm = MovementManager()

mm.initBoard()
time.sleep(0.5)

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
    mm.doHoming()
    mm.moveToPosSegmented(pos)

mm.waitForMovementFinished(2)
#mm.moveHome()


