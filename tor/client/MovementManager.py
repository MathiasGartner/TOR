import logging
log = logging.getLogger(__name__)

import math
import numpy as np
import re
import time

from tor.base.utils import Utils
import tor.client.ClientSettings as cs
from tor.client.Communicator import Communicator
from tor.client.Cords import Cords
from tor.client.InaManager import InaManager
from tor.client.Position import Position

class MovementManager:
    isInitialized = False
    currentPosition = Position(-1, -1, -1)

    def __init__(self):
        self.com = Communicator()
        self.feedratePercentage = 0
        self.magnetHadContact = False
        self.otpwCount = 0
        if cs.ON_RASPI:
            self.inaManager = InaManager()
        MovementManager.currentPosition = Position(-1, -1, -1) # todo: is this line needed?
        if not MovementManager.isInitialized:
            self.torMarlinVersion = "X"
            self.hasCorrectVersion = self.checkTORMarlinVersion()
            self.__initBoard()
            MovementManager.isInitialized = True

    def __initBoard(self):
        # Restore Settings
        #self.sendGCode("M501")
        # Set Feedrate Percentage
        self.setFeedratePercentage(cs.FR_DEFAULT)
        # enable all steppers
        self.sendGCode("M17")
        self.__updateCurrentPosition()
        self.waitForMovementFinished()
        self.clearOTPW()

    def sendGCode(self, cmd):
        log.debug("SEND: {}".format(cmd))
        self.com.send(cmd)
        msgs = self.com.recvUntilOk()
        return msgs

    def setFeedratePercentage(self, fr):
        self.sendGCode("M220 S{}".format(fr))
        self.feedratePercentage = fr

    def getCordLengthGCode(self, cords):
        cmd = ""
        if cords.isValid():
            cmd = "X{:f} Y{:f} Z{:f} E{:f}".format(cords.lengths[0], cords.lengths[1], cords.lengths[2], cords.lengths[3])
        else:
            log.warning("Cords are outside boundaries: {}".format(cords.lengths))
            raise Exception("Cords are outside boundaries: ", cords.lengths)
        return cmd

    def setCurrentPositionGCode(self, cords):
        cmd = "G92 " + self.getCordLengthGCode(cords)
        self.sendGCode(cmd)

    def __getCurrentPosition(self):
        pos = cs.HOME_POSITION
        cmd = "M114"
        msgs = self.sendGCode(cmd)
        if not cs.ON_RASPI:
            msgs = ["X:347.8965 Y:246.0000 Z:0.0000 E:246.0000 Count X:0 Y:13921 Z:19687"]
        pattern = "X:(\d+\.\d+) Y:(\d+\.\d+) Z:(\d+\.\d+) E:(\d+\.\d+) Count X:\d+ Y:\d+ Z:\d+"
        for msg in msgs:
            match = re.match(pattern, msg)
            if match:
                tmpCords = Cords([float(match.group(i)) for i in range(1, 5)])
                #INFO: modified cord lengths are not used here...
                pos = tmpCords.toPosition()
                print("new position from SKR board: {}".format(pos))
        return pos

    def __updateCurrentPosition(self):
        MovementManager.currentPosition = self.__getCurrentPosition()

    def checkTORMarlinVersion(self):
        versionOkay = False
        msgs = self.sendGCode("M115")
        if not cs.ON_RASPI:
            msgs = ["FIRMWARE_NAME:Marlin 2.0.5.3 (GitHub) TOR_VERSION:1.1 SOURCE_CODE_URL:https://github.com/MarlinFirmware/Marlin PROTOCOL_VERSION:1.0 MACHINE_TYPE:The Transparency of Randomness EXTRUDER_COUNT:1 UUID:cede2a2f-41a2-4748-9b12-c55c62f367ff"]
        pattern = ".*TOR_VERSION:(\d+\.\d+).*"
        for msg in msgs:
            match = re.match(pattern, msg)
            if match:
                self.torMarlinVersion = str(match.group(1))
        if self.torMarlinVersion == cs.TOR_MARLIN_VERSION:
            versionOkay = True
            log.info("TOR-Marlin v{} installed.".format(self.torMarlinVersion))
        else:
            versionOkay = False
            log.error("TOR-Marlin v{} installed, but v{} required.".format(self.torMarlinVersion, cs.TOR_MARLIN_VERSION))
        return versionOkay

    def clearOTPW(self):
        self.sendGCode("M912")

    def checkOTPW(self):
        otpwTriggered = False
        if cs.USE_OTPW:
            while True:
                otpwRegistered = False
                msgs = self.sendGCode("M911")
                if not cs.ON_RASPI:
                    msgs = ""
                for msg in msgs:
                    if "true" in msg:
                        otpwRegistered = True
                        break
                if otpwRegistered:
                    self.otpwCount += 1
                    log.info(f"OTPW registered, otpwCount: {self.otpwCount}")
                    self.clearOTPW()
                    time.sleep(cs.OTPW_WAIT_S)
                else:
                    self.otpwCount = 0
                    break
                    #log.info("no OTPW")
                if self.otpwCount >= cs.OTPW_MAX_COUNT:
                    otpwTriggered = True
                    log.info("OTPW triggered")
                    self.otpwCount = 0
                    break
        return otpwTriggered

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

    def enableSteppers(self):
        cmd = "M17"
        self.sendGCode(cmd)
        log.info("all stepper enabled")

    def disableSteppers(self):
        cmd = "M18"
        self.sendGCode(cmd)
        log.info("all stepper disabled")

    def setTopLed(self, brightness):
        if brightness < 0:
            brightness = 0
        elif brightness > 255:
            brightness = 255
        cmd = "M42 P40 S{} I".format(brightness)
        self.sendGCode(cmd)

    '''
    Homing modes
    0: full homing with repeated advances (corresponds to first mode 2 then mode 3)
    1: first go to center, then mode 0. do this only when position is nearly known!
    2: first tighten all cords, then move to anchor (default X) while pulling on other cords
    3: do repeated advances. need to be near anchor point 
    '''
    def doHoming(self, mode=0):
        cmd = cs.G_HOMING.format(mode)
        self.sendGCode(cmd)
        self.waitForMovementFinished()
        self.setCurrentPositionGCode(cs.HOME_POSITION.toCordLengths())
        MovementManager.currentPosition = cs.HOME_POSITION

    def __moveToCords(self, cords, segmented=False, useSlowDownStart=True, useSlowDownEnd=True):
        cmd = "G1 " + self.getCordLengthGCode(cords) + (" S" if segmented else "") + (" A" if not useSlowDownStart else "") + (" B" if not useSlowDownEnd else "")
        self.sendGCode(cmd)

    def moveToPos(self, pos, segmented=False, useSlowDownStart=True, useSlowDownEnd=True):
        if not isinstance(pos, list):
            pos = [pos]
        for p in pos:
            log.debug("MOVE{}: {} {} {}".format(" SEG" if segmented else "", p.x, p.y, p.z))
            cords = p.toCordLengths()
            self.__moveToCords(cords, segmented, useSlowDownStart, useSlowDownEnd)
            MovementManager.currentPosition = p

    def moveToXYZ(self, x, y, z, segmented=False, useSlowDownStart=True, useSlowDownEnd=True):
        pos = Position(x, y, z)
        self.moveToPos(pos, segmented, useSlowDownStart, )

    # first move to AFTER_HOMING_POSITION in a NOT segmented move
    def moveToPosAfterHoming(self, pos, segmented=False):
        self.setFeedratePercentage(cs.FR_SLOW_MOVE)
        self.moveToPos(cs.AFTER_HOMING_POSITION, segmented=False)
        self.waitForMovementFinished()
        self.setFeedratePercentage(cs.FR_DEFAULT)
        self.moveToPos(pos, segmented=segmented)

    # moveto parameter specifies if the movement is towards the ramp, moveto=False means movement is away from ramp
    def moveCloseToRamp(self, pos, segmented=False, moveto=True):
        if moveto:
            self.moveToPos(Position(pos.x,pos.y+cs.CRITICAL_AREA_APPROACH_Y,pos.z-cs.CRITICAL_AREA_APPROACH_Z), useSlowDownEnd=False, segmented=segmented)
            self.moveToPos(pos,useSlowDownStart=False, segmented=segmented)
        else:
            p0 = MovementManager.currentPosition
            self.moveToPos(Position(p0.x, p0.y + cs.CRITICAL_AREA_APPROACH_Y, p0.z - cs.CRITICAL_AREA_APPROACH_Z), useSlowDownEnd=False, segmented=segmented)
            self.moveToPos(pos,useSlowDownStart=False, segmented=segmented)

    def moveToXYPosDie(self, x, y, segmented=False, useSlowDownStart=True, useSlowDownEnd=True):
        pos = Position(x, y, cs.PICKUP_Z)
        self.moveToPos(pos, segmented, useSlowDownStart, )

    def moveToXPosRamp(self, x, segmented=False, useSlowDownStart=True, useSlowDownEnd=True):
        x = min(max(x, cs.RAMP_FORBIDDEN_X_MIN), cs.RAMP_FORBIDDEN_X_MAX)
        pos = Position(x, cs.RAMP_DROPOFF_Y, cs.RAMP_DROPOFF_Z)
        self.moveToPos(pos, segmented, useSlowDownStart, )

    def moveToXYPosDieAndRamp(self, x, y, segmented=False, useSlowDownStart=True, useSlowDownEnd=True):
        self.moveToXYPosDie(x, y, segmented, useSlowDownStart, )
        self.moveToXPosRamp(x, segmented, useSlowDownStart, )

    def moveHome(self, segmented=False, useSlowDownStart=True, useSlowDownEnd=True):
        self.moveToPos(cs.HOME_POSITION, segmented, useSlowDownStart, )

    def moveToParkingPosition(self, segmented=False, useSlowDownStart=True, useSlowDownEnd=True):
        self.moveToPos(cs.PARKING_POSITION, segmented, useSlowDownStart, )

    def moveToDeepParkingPosition(self, segmented=False, useSlowDownStart=True, useSlowDownEnd=True):
        self.moveToPos(cs.DEEP_PARKING_POSITION, segmented, useSlowDownStart, )

    def moveToAllCorners(self, segmented=False, useSlowDownStart=True, useSlowDownEnd=True):
        self.moveToPos(cs.CORNER_X, segmented, useSlowDownStart, )
        time.sleep(0.5)
        self.moveToPos(cs.CENTER_TOP, segmented, useSlowDownStart, )
        self.moveToPos(cs.CORNER_Z, segmented, useSlowDownStart, )
        time.sleep(0.5)
        self.moveToPos(cs.CENTER_TOP, segmented, useSlowDownStart, )
        self.moveToPos(cs.CORNER_E, segmented, useSlowDownStart, )
        time.sleep(0.5)
        self.moveToPos(cs.CENTER_TOP, segmented, useSlowDownStart, )
        self.moveToPos(cs.CORNER_Y, segmented, useSlowDownStart, )
        time.sleep(0.5)
        self.moveToPos(cs.CENTER_TOP, segmented, useSlowDownStart, )
        self.moveToPos(cs.CORNER_X, segmented, useSlowDownStart, )
        time.sleep(0.5)
        self.moveHome(segmented, useSlowDownStart, )

    def rollDie(self):
        log.info("die is now rolled...")
        log.info(f"t: {time.time()}")
        t1 = time.time() + cs.PULSE_MAGNET_TIME_MS / 2000.0
        t2 = time.time() + cs.PULSE_MAGNET_TIME_MS / 1000.0
        self.inaManager.wake()
        self.enableMagnet()
        Utils.sleepUntilTimestamp(t1)
        self.magnetHadContact = self.inaManager.magnetHasContact()
        Utils.sleepUntilTimestamp(t2)
        self.disableMagnet()
        self.inaManager.sleep()

    def waitForMovementFinished(self, sleepTime=0):
        self.sendGCode("M400")
        self.sendGCode("M118 A1 move finished")
        time.sleep(sleepTime)