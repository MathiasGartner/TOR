import math
import numpy as np
import time

import tor.client.ClientSettings as cs
from tor.client.Communicator import Communicator
from tor.client.Position import Position

class MovementManager:
    def __init__(self):
        self.com = Communicator()

    def initBoard(self):
        # Restore Settings
        self.sendGCode("M501")
        # Set Feedrate Percentage
        self.sendGCode("M220 S300")

    def sendGCode(self, cmd):
        print("SEND: " + cmd)
        self.com.send(cmd)
        self.com.recvUntilOk()

    def getCordLengthGCode(self, cords):
        cmd = ""
        if cords.isValid():
            cmd = "X{:f} Y{:f} Z{:f} E{:f}".format(cords.lengths[0], cords.lengths[1], cords.lengths[2], cords.lengths[3])
        else:
            raise Exception("Cords are outside boundaries: ", cords.lengths)
        return cmd

    def setCurrentPosition(self, cords):
        cmd = "G92 " + self.getCordLengthGCode(cords)
        self.sendGCode(cmd)

    def getCurrentPosition(self):
        # Get Current Position
        cmd = "M114"
        self.sendGCode(cmd)

    def moveToPos(self, pos):
        print("MOVE:", pos.x, pos.y, pos.z)
        cords = pos.toCordLengths()
        cmd = "G1 " + self.getCordLengthGCode(cords)
        self.sendGCode(cmd)

    def moveToXYZ(self, x, y, z):
        pos = Position(x, y, z)
        self.moveToPos(pos)

    def moveToXYPosDice(self, x, y):
        pos = Position(x, y, cs.PICKUP_Z)
        self.moveToPos(pos)

    def moveToXPosRamp(self, x):
        pos = Position(x, cs.RAMP_DROPOFF_Y, cs.RAMP_DROPOFF_Z)
        self.moveToPos(pos)

    def moveToXYPosDiceAndRamp(self, x, y):
        self.moveToXYPosDice(x, y)
        self.moveToXPosRamp(x)

    def moveHome(self):
        self.moveToPos(cs.HOME_POSITION)

    def moveToAllCorners(self):
        cX = Position(0, 0, 0)
        cY = Position(cs.LX, 0, 0)
        cZ = Position(cs.LX, cs.LY, 0)
        cE = Position(0, cs.LY, 0)
        self.moveToPos(cY)
        self.moveToPos(cZ)
        self.moveToPos(cE)
        self.moveToPos(cX)
        self.moveToPos(cZ)
        self.moveToPos(cY)
        self.moveToPos(cE)
        self.moveToPos(cX)
        self.moveHome()

    def rollDie(self):
        #TODO: implement
        print("dice is now rolled...")

    def searchForDie(self):
        dy = 5
        dyMoves = 2
        dx = 5
        y = cs.LY
        magnetToRampOffsetY = 5
        z = cs.PICKUP_Z
        xToZero = True
        while y > 0:
            x = 0 if xToZero else cs.LX
            self.moveToXYZ(x, y, z)
            xToZero = not xToZero
            while (xToZero and x > 0) or (not xToZero and x < cs.LX):
                x += -dx if xToZero else dx
                self.moveToXYZ(x, y, z)
            for _ in range(dyMoves):
                y -= dy
                self.moveToXYZ(x, y, z)
                overRampY = (cs.RAMP_END_Y + cs.MAGNET_RADIUS + magnetToRampOffsetY) - y
                if overRampY > 0:
                    z = cs.RAMP_END_Z - overRampY * np.tan(cs.RAMP_ALPHA)

    def waitForMovementFinished(self, sleepTime=0):
        self.sendGCode("M400")
        self.sendGCode("M118 A1 move finished")
        time.sleep(sleepTime)