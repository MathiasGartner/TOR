from tor.base.LogManager import getLogger
log = getLogger("MovementRoutines")

from datetime import datetime
import numpy as np
import time

from tor.base.DieRecognizer import DieRecognizer
from tor.base.DieRollResult import DieRollResult
from tor.base.utils import Utils
from tor.client import ClientSettings as cs
from tor.client.LedManager import LedManager
from tor.client.MovementManager import MovementManager
from tor.client.Position import Position

if cs.ON_RASPI:
    from tor.client.Camera import Camera

class MovementRoutines:
    def __init__(self, cm=None, mm=None):
        self.cm = cm
        if mm is None:
            self.mm = MovementManager()
        else:
            self.mm = mm
        self.dr = DieRecognizer()

    def loadPoints(self):
        return np.concatenate((cs.MESH_BED, cs.MESH_RAMP))

    def relativeBedCoordinatesToPosition(self, px, py):
        p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12 = self.loadPoints()
        # TODO: @David check the out of range logic. die was found correctly at y=1.002
        #       why is y < 0 allowed? is the calculation correct for py < 0?
        #       for now just clip
        minX = -0.1
        maxX = 1.1
        minY = -0.1
        maxY = 1.1
        if (px < minX or px > maxX or py < minY or py > maxY):
            log.warning("Out of range in relativeBedCoordinatesToPosition: [x,y]=[{},{}]".format(px, py))
            px = np.clip(px, minX, maxX)
            py = np.clip(py, minY, maxY)
        if (px < 0.5):
            x = (1 - py) * (p4[0] + px * (p6[0] - p4[0])) + py * (p1[0] + px * (p3[0] - p1[0]))
            y = (1 - 2 * px) * (p4[1] + py * (p1[1] - p4[1])) + 2 * px * (p5[1] + py * (p2[1] - p5[1]))
            z = (1 - 2 * px) * ((1 - py) * p4[2] + py * p1[2]) + 2 * px * ((1 - py) * p5[2] + py * p2[2])
        else:
            x = (1 - py) * (p6[0] + (1 - px) * (p4[0] - p6[0])) + py * (p3[0] + (1 - px) * (p1[0] - p3[0]))
            y = 2 * (1 - px) * (p5[1] + py * (p2[1] - p5[1])) + (2 * px - 1) * (p6[1] + py * (p3[1] - p6[1]))
            z = 2 * (1 - px) * ((1 - py) * p5[2] + py * p2[2]) + (2 * px - 1) * ((1 - py) * p6[2] + py * p3[2])
        return Position(x, y, z)

    def getSearchLines(self, points, mode):
        pass

    def searchForDie(self):
        # starting position
        '''
        1  2  3
        4  5  6
        --------
        7  8  9
        10 11 12
        M      M
        '''
        p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12 = self.loadPoints()
        n_rows = 4  # rows per area
        self.mm.moveToPos(Position(p1[0], p1[1], 100), True)
        self.mm.moveToPos(Position(p1[0], p1[1], p1[2]), True)
        self.mm.waitForMovementFinished()
        # raster bottom
        # mesh left side
        x_mesh_l = np.linspace(p1[0], p4[0], n_rows)
        y_mesh_l = np.linspace(p1[1], p4[1], n_rows)
        z_mesh_l = np.linspace(p1[2], p4[2], n_rows)
        # mesh center
        x_mesh_c = np.linspace(p2[0], p5[0], n_rows)
        y_mesh_c = np.linspace(p2[1], p5[1], n_rows)
        z_mesh_c = np.linspace(p2[2], p5[2], n_rows)
        # mesh right side
        x_mesh_r = np.linspace(p3[0], p6[0], n_rows)
        y_mesh_r = np.linspace(p3[1], p6[1], n_rows)
        z_mesh_r = np.linspace(p3[2], p6[2], n_rows)

        self.mm.setFeedratePercentage(cs.FR_SEARCH_BED)
        for i in range(n_rows):
            if (i % 2 == 0):
                self.mm.moveToPos(Position(x_mesh_l[i], y_mesh_l[i], z_mesh_l[i]), True)
                # self.mm.waitForMovementFinished()
                self.mm.moveToPos(Position(x_mesh_c[i], y_mesh_c[i], z_mesh_c[i]), True, useSlowDownEnd=False)
                # self.mm.waitForMovementFinished()
                self.mm.moveToPos(Position(x_mesh_r[i], y_mesh_r[i], z_mesh_r[i]), True, useSlowDownStart=False)
                self.mm.waitForMovementFinished()
            else:
                self.mm.moveToPos(Position(x_mesh_r[i], y_mesh_r[i], z_mesh_r[i]), True)
                # self.mm.waitForMovementFinished()
                self.mm.moveToPos(Position(x_mesh_c[i], y_mesh_c[i], z_mesh_c[i]), True, useSlowDownEnd=False)
                # self.mm.waitForMovementFinished()
                self.mm.moveToPos(Position(x_mesh_l[i], y_mesh_l[i], z_mesh_l[i]), True, useSlowDownStart=False)
                self.mm.waitForMovementFinished()
        self.mm.moveToPos(Position(MovementManager.currentPosition.x, MovementManager.currentPosition.y+cs.CRITICAL_AREA_APPROACH_Y, MovementManager.currentPosition.z-cs.CRITICAL_AREA_APPROACH_Z), True)

        #### ramp ###
        if cs.SEARCH_RAMP:
            # safely move away from ramp
            self.mm.moveToPos(Position(MovementManager.currentPosition.x, MovementManager.currentPosition.y + 20, 100), True)
            self.mm.waitForMovementFinished()

            # mesh left side
            x_mesh_l = np.linspace(p7[0], p10[0], n_rows)
            y_mesh_l = np.linspace(p7[1], p10[1], n_rows)
            z_mesh_l = np.linspace(p7[2], p10[2], n_rows)
            # mesh center
            x_mesh_c = np.linspace(p8[0], p11[0], n_rows)
            y_mesh_c = np.linspace(p8[1], p11[1], n_rows)
            z_mesh_c = np.linspace(p8[2], p11[2], n_rows)
            # mesh right side
            x_mesh_r = np.linspace(p9[0], p12[0], n_rows)
            y_mesh_r = np.linspace(p9[1], p12[1], n_rows)
            z_mesh_r = np.linspace(p9[2], p12[2], n_rows)

            self.mm.setFeedratePercentage(cs.FR_SEARCH_RAMP)
            for i in range(n_rows):
                if (i % 2 == 0):
                    self.mm.moveToPos(Position(x_mesh_l[i], y_mesh_l[i], z_mesh_l[i]), True)
                    self.mm.moveToPos(Position(x_mesh_c[i], y_mesh_c[i], z_mesh_c[i]), True)
                    self.mm.moveToPos(Position(x_mesh_r[i], y_mesh_r[i], z_mesh_r[i]), True)
                    self.mm.waitForMovementFinished()
                else:
                    self.mm.moveToPos(Position(x_mesh_r[i], y_mesh_r[i], z_mesh_r[i]), True)
                    self.mm.moveToPos(Position(x_mesh_c[i], y_mesh_c[i], z_mesh_c[i]), True)
                    self.mm.moveToPos(Position(x_mesh_l[i], y_mesh_l[i], z_mesh_l[i]), True)
                    self.mm.waitForMovementFinished()

        self.mm.setFeedratePercentage(cs.FR_DEFAULT)
        self.mm.moveToPos(cs.AFTER_PICKUP_POSITION, True)
        self.mm.waitForMovementFinished()

    def pickupDieFromPosition(self, pos, zOffset=0):
        if not isinstance(pos, list):
            pos = [pos]
        self.pickupWithMultiplePositions(pos, zOffset)

    def pickupWithMultiplePositions(self, positions, zOffset=0):
        self.mm.setFeedratePercentage(cs.FR_DEFAULT)
        self.mm.moveToPos(cs.BEFORE_PICKUP_POSITION, True)
        self.mm.waitForMovementFinished()

        pickupPos = None
        for pos in positions:
            log.debug("attempt to pick up at: {}".format(pos))
            pickupPos = self.relativeBedCoordinatesToPosition(pos.x, pos.y)
            if pickupPos.y > cs.RAMP_CRITICAL_Y:
                pickupPos.z += cs.EXTRA_Z_FOR_PICKUP
            pickupPos.z += zOffset
            log.debug("transformed pickupPos: {}".format(pickupPos))
            # move to pick-up position
            if pickupPos.y < cs.RAMP_CRITICAL_Y:
                self.mm.moveCloseToRamp(pickupPos, segmented=True)
            else:
                self.mm.moveToPos(pickupPos, True)
            self.mm.waitForMovementFinished()
            time.sleep(cs.WAIT_ON_PICKUP_POS)

        # move away from pick-up position
        if pickupPos.y < cs.RAMP_CRITICAL_Y:
            self.mm.moveCloseToRamp(cs.AFTER_PICKUP_POSITION, segmented=True, moveto=False)
        else:
            self.mm.moveToPos(cs.AFTER_PICKUP_POSITION, True)
        self.mm.waitForMovementFinished()

    def takePicture(self, cam=None, useTopLED=True):
        if cam is None:
            cam = Camera()
        if useTopLED:
            log.info("turn on top LED")
            self.mm.setTopLed(cs.LED_TOP_BRIGHTNESS)
        image = cam.takePicture()
        if useTopLED:
            log.info("turn off top LED")
            self.mm.setTopLed(cs.LED_TOP_BRIGHTNESS_OFF)
        cam.close()
        return image

    '''take a picture and locate the die'''
    def findDie(self, cam=None):
        image = self.takePicture(cam)
        dieRollResult, processedImages = self.dr.getDieRollResult(image, returnOriginalImg=True)
        return dieRollResult, processedImages

    '''
    take a picture and locate the die while homing is performed
    INFO: homing and camera can not be done in concurrent threads because both operations
    need to access the SKR board (G28 for homing and M42 for top LED)
    '''
    def findDieWhileHoming(self):
        log.info("do homing mode 2")
        self.mm.doHoming(mode=2)
        time.sleep(cs.WAIT_BEFORE_TAKE_PICTURE_WHILE_HOMING)
        cam = Camera(doWarmup=True)
        log.info("prepare camera: {}".format(cam))
        log.info("take picture while homing...")
        image = self.takePicture(cam)
        # log.info("image {}".format(image))
        log.info("do homing mode 3")
        self.mm.doHoming(mode=3)
        dieRollResult, processedImages = self.dr.getDieRollResult(image, returnOriginalImg=True)
        log.info("result: {}".format(dieRollResult))
        return dieRollResult, processedImages

    def pickupDieWhileHoming(self):
        dieRollResult, processedImages = self.findDieWhileHoming()
        self.mm.waitForMovementFinished()
        self.mm.moveToPosAfterHoming(cs.CENTER_TOP, True)
        if dieRollResult.found:
            log.info("pickup after homing")
            self.pickupDieFromPosition(dieRollResult.position)
        return dieRollResult

    def pickupDie_takeImage(self, cam=None):
        dieRollResult = DieRollResult()
        if cs.USE_IMAGE_RECOGNITION:
            dieRollResult, processedImages = self.findDie(cam)
            log.debug("result: {}".format(dieRollResult.result))
            if cs.STORE_IMAGES or (cs.STORE_IMAGES_NOT_FOUND and not dieRollResult.found):
                self.dr.writeDiceImages(clientId=self.cm.clientId, images=processedImages, found=dieRollResult.found, timestamp=Utils.getFilenameTimestamp())
        return dieRollResult

    def pickupDie_pickup(self, dieRollResult, onSendResult=None, zOffset=0):
        if dieRollResult.found:
            log.info("dieRollResult: {}".format(dieRollResult))
            if cs.SHOW_DIE_RESULT_WITH_LEDS:
                lm = LedManager()
                lm.showResult(dieRollResult.result)
            if onSendResult is not None:
                onSendResult(dieRollResult)
            self.pickupDieFromPosition(dieRollResult.position, zOffset)
        else:
            log.warning("Position for pickup not known.")

    def pickupDie_sideways(self, dieRollResult):
        if dieRollResult.found:
            log.info("dieRollResult: {}".format(dieRollResult))
            left = dieRollResult.position
            left.y = Utils.clamp(left.y + cs.SIDEWAYS_PICKUP_Y_OFFSET, 0.0, 1.0)
            right = dieRollResult.position
            right.y = Utils.clamp(right.y - cs.SIDEWAYS_PICKUP_Y_OFFSET, 0.0, 1.0)
            self.pickupDieFromPosition([left, right])
        else:
            log.warning("Position for pickup not known.")

    def pickupDie(self, onSendResult=None, cam=None):
        dieRollResult = self.pickupDie_takeImage(cam)
        if dieRollResult.found:
            self.pickupDie_pickup(dieRollResult, onSendResult)
        else:
            log.info("Start search routine.")
            self.searchForDie()
        return dieRollResult

    def getDropoffAdvancePosition(self, pos, stage=1):
        if stage == 1:
            p = Position(pos[0], pos[1] + cs.DROPOFF_ADVANCE_OFFSET_Y, pos[2] + cs.DROPOFF_ADVANCE_OFFSET_Z)
        elif stage == 2:
            p = Position(pos[0], pos[1] + cs.DROPOFF_ADVANCE_OFFSET_Y2, pos[2] + cs.DROPOFF_ADVANCE_OFFSET_Z2)
        return p

    def moveToDropoffPosition(self, dropoffPos, speedupFactor1=1.0, speedupFactor2=1.0):
        self.mm.setFeedratePercentage(cs.FR_DEFAULT)
        if not isinstance(dropoffPos, Position):
            dropoffPos = Position(dropoffPos[0], dropoffPos[1], dropoffPos[2])
        dropoffAdvancePos = self.getDropoffAdvancePosition(dropoffPos, stage=1)
        dropoffAdvancePos2 = self.getDropoffAdvancePosition(dropoffPos, stage=2)
        self.mm.moveToPos(dropoffAdvancePos, True)
        self.mm.setFeedratePercentage(cs.FR_DROPOFF_ADVANCE * speedupFactor1)
        self.mm.moveToPos(dropoffAdvancePos2, True)
        self.mm.setFeedratePercentage(cs.FR_DROPOFF_ADVANCE_SLOW * speedupFactor2)
        self.mm.moveToPos(dropoffPos, True)
        self.mm.waitForMovementFinished()
        self.mm.setFeedratePercentage(cs.FR_DEFAULT)

    def getDropoffPosByPercent(self, percent, invert=False):
        dropoffPos = cs.MESH_MAGNET[3, :]
        percent = np.clip(percent, 0.0, 1.0)
        if invert:
            px = np.clip(1 - percent, 0.0, 1.0)
        else:
            px = percent
        if px < 0.5:
            if not cs.USE_MAGNET_BETWEEN_P0P1:
                px = 1 - px
        elif not cs.USE_MAGNET_BETWEEN_P2P3:
            px = 1 - px

        if cs.ALWAYS_USE_PX >= 0 and cs.ALWAYS_USE_PX <= 3:
            # log.info("use fixed magnet point")
            dropoffPos = cs.MESH_MAGNET[cs.ALWAYS_USE_PX, :]
        else:
            if px < 0.5:
                dropoffPos = 2 * px * cs.MESH_MAGNET[1, :] + (1 - 2 * px) * cs.MESH_MAGNET[0, :]
            else:
                dropoffPos = 2 * (px - 0.5) * cs.MESH_MAGNET[3, :] + 2 * (1 - px) * cs.MESH_MAGNET[2, :]
        return dropoffPos

    def getDropoffPosByXCoordinate(self, x, invert=False):
        percent = x / cs.LX
        return self.getDropoffPosByPercent(percent, invert)

    def run(self, lastPickupX, numFailedTries=0):
        # calculate dropoff position
        # on every second try the position is not inverted
        invert = (numFailedTries % 2) == 0
        # if the first two tries fail, the position is altered
        if numFailedTries >= 2:
            lastPickupX = lastPickupX / (numFailedTries // 2)
        dropoffPos = self.getDropoffPosByPercent(lastPickupX, invert=invert)

        # move to dropoff position
        self.moveToDropoffPosition(dropoffPos)

        # TODO: why is this not working?
        # cam = Camera(doWarmup=False)

        # roll die
        time.sleep(cs.WAIT_BEFORE_ROLL_TIME)
        self.mm.rollDie()
        time.sleep(cs.DIE_ROLL_TIME / 2.0)
        self.mm.setFeedratePercentage(cs.FR_DEFAULT)
        self.mm.moveToPos(cs.CENTER_TOP, True)
        time.sleep(cs.DIE_ROLL_TIME / 2.0)

        return dropoffPos

    def doQuickRoll(self):
        dropoffPos = self.getDropoffPosByPercent(0.1, invert=True)
        self.moveToDropoffPosition(dropoffPos)
        time.sleep(cs.WAIT_BEFORE_ROLL_TIME)
        self.mm.rollDie()
        time.sleep(cs.WAIT_BEFORE_ROLL_TIME)
        self.mm.setFeedratePercentage(cs.FR_DEFAULT)
        self.mm.moveToPos(cs.CENTER_TOP, True)

    def rollDie(self, dropoffPos):
        self.moveToDropoffPosition(dropoffPos)

        time.sleep(cs.WAIT_BEFORE_ROLL_TIME)
        self.mm.rollDie()
        time.sleep(cs.DIE_ROLL_TIME / 2.0)
        self.mm.setFeedratePercentage(cs.FR_DEFAULT)
        self.mm.moveToPos(cs.CENTER_TOP, True)
        self.mm.waitForMovementFinished()

    def moveToPosAndTakeMagnetVerificationImage(self, pos):
        self.mm.setFeedratePercentage(cs.FR_SLOW_MOVE)
        self.mm.moveToPos(pos, True)
        self.mm.setFeedratePercentage(cs.FR_DEFAULT)
        self.mm.waitForMovementFinished(0.5)
        im = self.takePicture(cam=None, useTopLED=False)
        im = self.dr.transformImageForMagnetPositionVerification(im)
        return im

    def verifyMagnetPosition(self, pos=cs.VERIFY_MAGNET_POSITION):
        im = self.moveToPosAndTakeMagnetVerificationImage(pos)
        isOK = self.cm.askMagnetPositionIsOK(im)
        if isOK:
            log.info("Position verified")
            self.mm.moveToPos(cs.CENTER_TOP, True)
            self.mm.waitForMovementFinished()
        else:
            log.warning("Position could not be verified!")
        return isOK

    def wiggleOnCurrentPos(self):
        dz = 4
        posMoveUpAndDown = self.mm.currentPosition + Position(0, 0, dz)
        self.mm.moveToPos(posMoveUpAndDown)
        self.mm.waitForMovementFinished()
        posMoveUpAndDown = self.mm.currentPosition + Position(0, 0, -1.5 * dz)
        self.mm.moveToPos(posMoveUpAndDown)
        self.mm.waitForMovementFinished()
        posMoveUpAndDown = self.mm.currentPosition + Position(0, 0, 1.5 * dz)
        self.mm.moveToPos(posMoveUpAndDown)
        self.mm.waitForMovementFinished()
        posMoveUpAndDown = self.mm.currentPosition + Position(0, 0, -2 * dz)
        self.mm.moveToPos(posMoveUpAndDown)
        self.mm.waitForMovementFinished()

    def checkSuccessfulHoming(self):
        positionOK = self.verifyMagnetPosition()
        if positionOK:
            log.info("homing successful")
        else:
            log.warning("could not verify position after homing")
            self.mm.disableSteppers()
            time.sleep(2)
            self.wiggleOnCurrentPos()
            self.mm.disableSteppers()
            time.sleep(2)
            self.wiggleOnCurrentPos()
            time.sleep(2)
            self.mm.doHoming()
            self.mm.moveToPosAfterHoming(cs.CENTER_TOP, True)
            self.mm.waitForMovementFinished()
            positionOK = self.verifyMagnetPosition()
            if positionOK:
                log.warning("homing successful (second attempt).")
            else:
                log.warning("could not verify position after homing two times")
        return positionOK

    def getValidUserPosition(self, pos):
        validPos = Position(Utils.clamp(pos.x, 0, cs.LX), Utils.clamp(pos.y, 160, cs.LY), Utils.clamp(pos.z, 50, 220))
        return validPos

    def performUserAction(self, action, steps):
        if action != "NONE":
            log.info("perform action: {},{}".format(action, steps))
        posFrom = self.mm.currentPosition
        posTo = None
        try:
            steps = int(steps)
        except ValueError:
            steps = 0
        if action == "DOWN":
            log.info("move down")
            posTo = posFrom + Position(0, 0, int(steps))
        elif action == "UP":
            log.info("move up")
            posTo = posFrom + Position(0, 0, -int(steps))
        elif action == "LEFT":
            log.info("move left")
            posTo = posFrom + Position(int(steps), 0, 0)
        elif action == "RIGHT":
            log.info("move right")
            posTo = posFrom + Position(-int(steps), 0, 0)
        elif action == "FRONT":
            log.info("move front")
            posTo = posFrom + Position(0, int(steps), 0)
        elif action == "BACK":
            log.info("move back")
            posTo = posFrom + Position(0, -int(steps), 0)
        elif action == "ROLL":
            log.info("roll die")
            self.mm.moveToPos(cs.AFTER_PICKUP_POSITION, True)
            dropoffPosPercent = int(steps)
            dropoffPos = self.getDropoffPosByPercent(1.0 - (dropoffPosPercent / 100.0), invert=False)
            # dropoffPos = cs.MESH_MAGNET[2]
            self.rollDie(dropoffPos)
            dieRollResult, processedImages = self.findDie()
            if dieRollResult.found:
                log.info("dieRollResult: {}".format(dieRollResult))
                self.cm.sendDieRollResult(dieRollResult, userGenerated=True)
            else:
                log.info("die not found...")
        else:
            # log.warning("Action {} not known.".format(action))
            time.sleep(0.7 * cs.ASK_EVERY_NTH_SECOND_FOR_JOB_USERMODE)
        if posTo is not None:
            validPos = self.getValidUserPosition(posTo)
            self.mm.moveToPos(validPos, True)
            self.mm.waitForMovementFinished()

    def doTestPerformance(self, startTime):
        log.info("start performance")
        startTimestamp = datetime.timestamp(startTime)
        timings = np.cumsum([0, 2, 6.5, 3, 20, 2])
        timestamps = [t + startTimestamp for t in timings]
        log.info(timestamps)
        lm = LedManager()

        step = 0
        Utils.sleepUntilTimestampIndex(step, timestamps)
        for i in range(15):
            lm.setLeds(range(0, i * 5), 255, 255, 255)
            time.sleep(0.05)
            lm.clear()
            time.sleep(0.05)

        step += 1
        Utils.sleepUntilTimestampIndex(step, timestamps)
        for i in range(10):
            lm.setLeds(range(0, i*5), i*10, i*3, i)
            time.sleep(0.5)

        step += 1
        Utils.sleepUntilTimestampIndex(step, timestamps)
        self.mm.moveToPos(cs.BEFORE_PICKUP_POSITION, True)

        step += 1
        Utils.sleepUntilTimestampIndex(step, timestamps)
        self.searchForDie()

        step += 1
        Utils.sleepUntilTimestampIndex(step, timestamps)
        self.mm.moveToPos(cs.BEFORE_PICKUP_POSITION, True)

    def doDieRollAndPickupPerformance(self, startTime):
        log.info("preparing for performance...")
        self.pickupDie()
        lm = LedManager()
        lm.clear()
        self.mm.setFeedratePercentage(cs.FR_SLOW_MOVE)
        # TODO: check if USE_MAGNET_BETWEEN_P0P1=True, otherwise use left side
        dropoffPos = cs.MESH_MAGNET[2]
        dropoffAdvancePos = Position(dropoffPos[0], dropoffPos[1] + cs.DROPOFF_ADVANCE_OFFSET_Y, dropoffPos[2] + cs.DROPOFF_ADVANCE_OFFSET_Z)
        self.mm.moveToPos(dropoffAdvancePos, True)
        fr_factor = 2
        fr_default_old = cs.FR_DEFAULT
        cs.FR_DEFAULT = cs.FR_DEFAULT * fr_factor
        log.info("in starting position...")
        log.info("waiting for performance to start...")
        startTimestamp = datetime.timestamp(startTime)
        timings = np.cumsum([0,
                             0.25,      # turn on leds
                             6.0,       # move to dropoff position
                             2,         # roll die and move to cs.CENTER_TOP
                             0.9+4.2,   # take picture
                             0.3,       # move to cs.BEFORE_PICKUP_POSITION
                             5.1,       # find die on image
                             4.9        # pickup die
                            ])          # move to starting position (dropoff advance position)
        timestamps = [t + startTimestamp for t in timings]
        log.info(timestamps)

        step = 0
        Utils.sleepUntilTimestampIndex(step, timestamps)
        # cam = Camera(doWarmup=False)
        lm.setAllLeds()

        step += 1
        Utils.sleepUntilTimestampIndex(step, timestamps)
        self.moveToDropoffPosition(cs.MESH_MAGNET[2], speedupFactor1=1.5, speedupFactor2=1)
        # self.moveToDropoffPosition(cs.MESH_MAGNET[2], speedupFactor1=3, speedupFactor2=3)

        step += 1
        Utils.sleepUntilTimestampIndex(step, timestamps)
        self.mm.setFeedratePercentage(cs.FR_DEFAULT)
        self.mm.rollDie()
        time.sleep(0.4)
        self.mm.moveToPos(cs.CENTER_TOP, True)

        step += 1
        Utils.sleepUntilTimestampIndex(step, timestamps)
        # image = self.takePicture(cam)
        image = self.takePicture()

        step += 1
        Utils.sleepUntilTimestampIndex(step, timestamps)
        self.mm.moveToPos(cs.BEFORE_PICKUP_POSITION, True)

        step += 1
        Utils.sleepUntilTimestampIndex(step, timestamps)
        dieRollResult, _ = self.dr.getDieRollResult(image, returnOriginalImg=True)

        step += 1
        Utils.sleepUntilTimestampIndex(step, timestamps)
        if dieRollResult.found:
            self.pickupDieFromPosition(dieRollResult.position)
        else:
            self.searchForDie()

        step += 1
        Utils.sleepUntilTimestampIndex(step, timestamps)
        self.mm.moveToPos(dropoffAdvancePos, True)
        lm.clear()

        cs.FR_DEFAULT = fr_default_old

    def doPositionTestWithTiming(self, startTime, clientIdentity, x, y, z):
        log.info("preparing for performance...")
        lm = LedManager()
        lm.clear()
        self.mm.setTopLed(cs.LED_TOP_BRIGHTNESS_OFF)
        log.info("waiting for performance to start...")
        startTimestamp = datetime.timestamp(startTime)
        timings = np.cumsum([clientIdentity["Position"]*0.2,  # wait for position to be next
                             27 * 0.2 + 1])  # light up
        timestamps = [t + startTimestamp for t in timings]
        log.info(timestamps)

        step = 0
        Utils.sleepUntilTimestampIndex(step, timestamps)
        p = int(clientIdentity["Position"])
        f = x + y + z
        r = cs.LED_STRIP_DEFAULT_COLOR[0] + 10 * f
        g = cs.LED_STRIP_DEFAULT_COLOR[1] - 8 * f
        b = cs.LED_STRIP_DEFAULT_COLOR[2]
        lm.setAllLeds(r=r, g=g, b=b)

        step += 1
        Utils.sleepUntilTimestampIndex(step, timestamps)
        lm.clear()

    def doLightTest(self, startTime):
        log.info("preparing for performance...")
        lm = LedManager()
        lm.clear()
        self.mm.setTopLed(cs.LED_TOP_BRIGHTNESS_OFF)
        log.info("waiting for performance to start...")
        startTimestamp = datetime.timestamp(startTime)
        timings = np.cumsum([0])
        timestamps = [t + startTimestamp for t in timings]
        log.info(timestamps)

        step = 0
        Utils.sleepUntilTimestampIndex(step, timestamps)
        for r in range(0, 150, 10):
            for g in range(0, 150, 10):
                for b in range(0, 150, 10):
                    lm.setAllLeds(r=r, g=g, b=b)
                    log.info("r={}, g={}, b={}".format(r, g, b))
                    time.sleep(1)

    def doRollDie(self, startTime):
        log.info("preparing for performance...")
        log.info("waiting for performance to start...")
        startTimestamp = datetime.timestamp(startTime)
        timings = np.cumsum([0])
        timestamps = [t + startTimestamp for t in timings]
        log.info(timestamps)

        step = 0
        Utils.sleepUntilTimestampIndex(step, timestamps)
        dropoffPos = cs.MESH_MAGNET[2, :]
        self.moveToDropoffPosition(dropoffPos)

        # roll die
        time.sleep(cs.WAIT_BEFORE_ROLL_TIME)
        self.mm.rollDie()
        time.sleep(cs.DIE_ROLL_TIME / 2.0)
        self.mm.setFeedratePercentage(cs.FR_DEFAULT)
        self.mm.moveToPos(cs.CENTER_TOP, True)
        time.sleep(cs.DIE_ROLL_TIME / 2.0)

    def getLastMagnetContactStatus(self):
        return self.mm.magnetHadContact
