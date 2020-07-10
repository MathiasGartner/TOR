import math
import numpy as np
import re
import time

import tor.client.ClientSettings as cs
from tor.client.Communicator import Communicator
from tor.client.Cords import Cords
from tor.client.Position import Position

class MovementManager:
    def __init__(self):
        self.com = Communicator()

    def initBoard(self):
        # Restore Settings
        #self.sendGCode("M501")
        # Set Feedrate Percentage
        self.setFeedratePercentage(cs.FEEDRATE_PERCENTAGE)
        # enable all steppers
        self.sendGCode("M17")
        self.updateCurrentPosition()

    def setFeedratePercentage(self, fr):
        self.sendGCode("M220 S{}".format(fr))

    def sendGCode(self, cmd):
        print("SEND: " + cmd)
        self.com.send(cmd)
        msgs = self.com.recvUntilOk()
        return msgs

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
        pos = cs.HOME_POSITION
        cmd = "M114"
        msgs = self.sendGCode(cmd)
        if not cs.ON_RASPI:
            msgs = ["X:347.8965 Y:246.0000 Z:0.0000 E:246.0000 Count X:0 Y:13921 Z:19687"]
        pattern = "X:(\d+\.\d+) Y:(\d+\.\d+) Z:(\d+\.\d+) E:(\d+\.\d+) Count X:\d+ Y:\d+ Z:\d+"
        for msg in msgs:
            match = re.match(pattern, msg)
            if match:
                pos = Cords([float(match.group(i)) for i in range(1, 5)]).toPosition()
        return pos

    def updateCurrentPosition(self):
        self.currentPosition = self.getCurrentPosition()

    def toggleLED(self, ledId, isOn, r=0, b=0, g=0, brightness=255):
        raise Exception("LEDs are not supported")
        if not isOn:
            r = b = g = 0
        cmd = "M150 N{} R{} U{} B{} P{}".format(ledId, r, g, b, brightness)
        self.sendGCode(cmd)

    def enableMagnet(self):
        cmd = "M42 P41 S255"
        self.sendGCode(cmd)

    def disableMagnet(self):
        cmd = "M42 P41 S0"
        self.sendGCode(cmd)

    def pulseMagnet(self):
        cmd = "M43 T I S41 L41 R1 W{}".format(cs.PULSE_MAGNET_TIME_MS)
        self.sendGCode(cmd)

    def setLed(self, brightness):
        if brightness < 0:
            brightness = 0
        elif brightness > 255:
            brightness = 255
        cmd = "M42 P40 S{} I".format(brightness)
        self.sendGCode(cmd)

    def doHoming(self):
        #cmd = "G28 N0 A0 P140 S70"
        cmd = "G28 A0 S50 P140 F68 R8 D1.05 B1.15"
        self.sendGCode(cmd)
        self.waitForMovementFinished()
        self.updateCurrentPosition()

    def moveToCords(self, cords, segmented=False):
        cmd = "G1 " + self.getCordLengthGCode(cords) + (" S" if segmented else "")
        self.sendGCode(cmd)

    def moveToPos(self, pos, segmented=False):
        if not isinstance(pos, list):
            pos = [pos]
        for p in pos:
            print("MOVE{}:".format(" SEG" if segmented else ""), p.x, p.y, p.z)
            cords = p.toCordLengths()
            self.moveToCords(cords, segmented)
            self.currentPosition = p

    #TODO: remove, should only be done in Marlin and not on external client. use "G1 S ..." command
    def moveToPosSegmented(self, pos):
        self.moveToPos(pos, True)
        """
        startPos = self.currentPosition
        diffPos = pos - startPos
        unitsPerSegment = 10.0
        length = diffPos.norm()
        segmentCount = math.floor(length / unitsPerSegment)
        segmentCount = max(segmentCount, 1)
        segmentChange = diffPos / segmentCount
        nextPos = startPos + segmentChange
        segmentedPositions = []
        for i in range(1, segmentCount):
            segmentedPositions.append(nextPos)
            nextPos = nextPos + segmentChange
        segmentedPositions.append(pos)
        self.moveToPos(segmentedPositions)
        """

    def moveToXYZ(self, x, y, z, segmented=False):
        pos = Position(x, y, z)
        self.moveToPos(pos, segmented)

    def moveToXYPosDie(self, x, y, segmented=False):
        pos = Position(x, y, cs.PICKUP_Z)
        self.moveToPos(pos, segmented)

    def moveToXPosRamp(self, x, segmented=False):
        x = min(max(x, cs.RAMP_FORBIDDEN_X_MIN), cs.RAMP_FORBIDDEN_X_MAX)
        pos = Position(x, cs.RAMP_DROPOFF_Y, cs.RAMP_DROPOFF_Z)
        self.moveToPos(pos, segmented)

    def moveToXYPosDieAndRamp(self, x, y, segmented=False):
        self.moveToXYPosDie(x, y, segmented)
        self.moveToXPosRamp(x, segmented)

    def moveHome(self, segmented=False):
        self.moveToPos(cs.HOME_POSITION, segmented)

    def moveToAllCorners(self, segmented=False):
        self.moveToPos(cs.CORNER_X, segmented)
        time.sleep(0.5)
        self.moveToPos(cs.CENTER_TOP, segmented)
        self.moveToPos(cs.CORNER_Z, segmented)
        time.sleep(0.5)
        self.moveToPos(cs.CENTER_TOP, segmented)
        self.moveToPos(cs.CORNER_E, segmented)
        time.sleep(0.5)
        self.moveToPos(cs.CENTER_TOP, segmented)
        self.moveToPos(cs.CORNER_Y, segmented)
        time.sleep(0.5)
        self.moveToPos(cs.CENTER_TOP, segmented)
        self.moveToPos(cs.CORNER_X, segmented)
        time.sleep(0.5)
        self.moveHome(segmented)

    def rollDie(self):
        print("die is now rolled...")
        self.pulseMagnet()

    def searchForDie(self):
        x = 0
        minY = 20
        dy = 40
        y = cs.LY
        magnetToRampOffsetY = 5
        z = cs.PICKUP_Z
        xToZero = True
        self.moveToXYZ(x, y, z)
        self.waitForMovementFinished()
        while y > (dy + minY):
            x = 0 if xToZero else cs.LX
            self.moveToXYZ(x, y, z, segmented=True)
            self.waitForMovementFinished()
            #time.sleep(1)
            xToZero = not xToZero
            x = 0 if xToZero else cs.LX
            self.moveToXYZ(x, y, z, segmented=True)
            self.waitForMovementFinished()
            time.sleep(1)
            y -= dy
            overRampY = (cs.RAMP_END_Y + cs.MAGNET_RADIUS + magnetToRampOffsetY) - y
            if overRampY > 0:
                z = cs.RAMP_END_Z - overRampY * np.tan(cs.RAMP_ALPHA)
        self.moveToPos(cs.CENTER_TOP)

    def waitForMovementFinished(self, sleepTime=0):
        self.sendGCode("M400")
        self.sendGCode("M118 A1 move finished")
        time.sleep(sleepTime)