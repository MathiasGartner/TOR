#!/usr/bin/env python3

import sys
import time

import tor.client.ClientSettings as cs
from tor.client.MovementManager import MovementManager
from tor.client.Position import Position

mm = MovementManager()

mm.initBoard()
mm.setCurrentPosition(cs.HOME_CORDS)
mm.getCurrentPosition()
time.sleep(0.5)

mode = 4
if len(sys.argv) > 1:
    mode=int(sys.argv[1])
print("mode: ", mode)

if mode == 0:
    dicePosition = Position(100, 30, 210)
    mm.moveToPos(cs.HOME_POSITION)
    mm.moveToPos(dicePosition)
    mm.moveToPos(cs.HOME_POSITION)

    diceX = 120
    diceY = 160
    mm.moveToXYPosDice(diceX, diceY)
    mm.waitForMovementFinished(0.5)
    mm.moveToYPosRamp(diceY)

elif mode == 1: #move to x y and pick up dice
    diceX = int(sys.argv[2])
    diceY = int(sys.argv[3])
    mm.moveToXYPosDice(diceX, diceY)
    mm.waitForMovementFinished(0.5)
    mm.moveToYPosRamp(diceY)

elif mode == 2: #move to x y z
    pos = Position(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    mm.moveToPos(pos)

elif mode == 3: #move to all corners
    cX = Position(0, 0, 0)
    cY = Position(0, cs.LY, 0)
    cZ = Position(cs.LX, cs.LY, 0)
    cE = Position(cs.LX, 0, 0)
    mm.moveToPos(cY)
    mm.moveToPos(cZ)
    mm.moveToPos(cE)
    mm.moveToPos(cX)

elif mode == 4: #search for dice
    mm.searchForDice()
    mm.moveToYPosRamp(cs.LY/2)

mm.waitForMovementFinished(2)
mm.moveHome()


