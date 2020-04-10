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

    def moveToYPosRamp(self, y):
        pos = Position(cs.RAMP_DROPOFF_X, y, cs.RAMP_DROPOFF_Z)
        self.moveToPos(pos)

    def moveHome(self):
        self.moveToPos(cs.HOME_POSITION)

    def searchForDice(self):
        dx = 5
        dxMoves = 2
        dy = 5
        x = cs.LX
        z = cs.PICKUP_Z
        yToZero = True
        while x > 0:
            y = 0 if yToZero else cs.LY
            self.moveToXYZ(x, y, z)
            yToZero = not yToZero
            while (yToZero and y > 0) or (not yToZero and y < cs.LY):
                y += -dy if yToZero else dy
                self.moveToXYZ(x, y, z)
            for _ in range(dxMoves):
                x -= dx
                self.moveToXYZ(x, y, z)
                overRampX = (cs.RAMP_END_X + cs.MAGNET_RADIUS) - x
                if overRampX > 0:
                    z = cs.RAMP_END_Z - overRampX * np.tan(cs.RAMP_ALPHA)

    def waitForMovementFinished(self, sleepTime=0):
        self.sendGCode("M400")
        self.sendGCode("M118 A1 move finished")
        time.sleep(sleepTime)