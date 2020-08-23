import logging
log = logging.getLogger(__name__)

from datetime import datetime
import numpy as np
import time

from tor.base.DieRecognizer import DieRecognizer
from tor.base.DieRollResult import DieRollResult
from tor.client import ClientSettings as cs
from tor.client.LedManager import LedManager
from tor.client.MovementManager import MovementManager
from tor.client.Position import Position

if cs.ON_RASPI:
    from tor.client.Camera import Camera

class MovementRoutines:
    def __init__(self):
        self.mm = MovementManager()
        self.dr = DieRecognizer()

    def loadPoints(self):
        return np.concatenate((cs.MESH_BED, cs.MESH_RAMP))

    def relativeBedCoordinatesToPosition(self, px, py):
        p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12 = self.loadPoints()
        #TODO: check the out of range logic. die was found correctly at y=1.002
        if (px < 0 or px > 1 or py < -0.1 or py > 1):
            log.warning("Out of range in relativeBedCoordinatesToPosition: [x,y]=[{},{}]".format(px, py))
            return cs.BEFORE_PICKUP_POSITION
        if (px < 0.5):
            x = (1 - py) * (p4[0] + px * (p6[0] - p4[0])) + py * (p1[0] + px * (p3[0] - p1[0]))
            y = (1 - 2 * px) * (p4[1] + py * (p1[1] - p4[1])) + 2 * px * (p5[1] + py * (p2[1] - p5[1]))
            z = (1 - 2 * px) * ((1 - py) * p4[2] + py * p1[2]) + 2 * px * ((1 - py) * p5[2] + py * p2[2])
        else:
            x = (1 - py) * (p6[0] + (1 - px) * (p4[0] - p6[0])) + py * (p3[0] + (1 - px) * (p1[0] - p3[0]))
            y = 2 * (1 - px) * (p5[1] + py * (p2[1] - p5[1])) + (2 * px - 1) * (p6[1] + py * (p3[1] - p6[1]))
            z = 2 * (1 - px) * ((1 - py) * p5[2] + py * p2[2]) + (2 * px - 1) * ((1 - py) * p6[2] + py * p3[2])
        return Position(x, y, z)

    def searchForDie(self):
        #starting position
        '''
        1  2  3
        4  5  6
        --------
        7  8  9
        10 11 12
        M      M
        '''
        p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12 = self.loadPoints()
        n_rows = 4 # rows per area
        self.mm.moveToPos(Position(p1[0], p1[1], 100), True)
        self.mm.moveToPos(Position(p1[0], p1[1], p1[2]), True)
        self.mm.waitForMovementFinished()
        #raster bottom
        # mesh left side
        x_mesh_l=np.linspace(p1[0], p4[0], n_rows)
        y_mesh_l=np.linspace(p1[1], p4[1], n_rows)
        z_mesh_l=np.linspace(p1[2], p4[2], n_rows)
        #mesh center
        x_mesh_c = np.linspace(p2[0], p5[0], n_rows)
        y_mesh_c = np.linspace(p2[1], p5[1], n_rows)
        z_mesh_c = np.linspace(p2[2], p5[2], n_rows)
        #mesh right side
        x_mesh_r = np.linspace(p3[0], p6[0], n_rows)
        y_mesh_r = np.linspace(p3[1], p6[1], n_rows)
        z_mesh_r = np.linspace(p3[2], p6[2], n_rows)

        self.mm.setFeedratePercentage(cs.FR_SEARCH_BED)
        for i in range(n_rows):
            if (i % 2 == 0):
                self.mm.moveToPos(Position(x_mesh_l[i], y_mesh_l[i], z_mesh_l[i]), True)
                #self.mm.waitForMovementFinished()
                self.mm.moveToPos(Position(x_mesh_c[i], y_mesh_c[i], z_mesh_c[i]), True, useSlowDownEnd=False)
                #self.mm.waitForMovementFinished()
                self.mm.moveToPos(Position(x_mesh_r[i], y_mesh_r[i], z_mesh_r[i]), True, useSlowDownStart=False)
                self.mm.waitForMovementFinished()
            else:
                self.mm.moveToPos(Position(x_mesh_r[i], y_mesh_r[i], z_mesh_r[i]), True)
                #self.mm.waitForMovementFinished()
                self.mm.moveToPos(Position(x_mesh_c[i], y_mesh_c[i], z_mesh_c[i]), True, useSlowDownEnd=False)
                #self.mm.waitForMovementFinished()
                self.mm.moveToPos(Position(x_mesh_l[i], y_mesh_l[i], z_mesh_l[i]), True, useSlowDownStart=False)
                self.mm.waitForMovementFinished()
        self.mm.moveToPos(Position(MovementManager.currentPosition.x, MovementManager.currentPosition.y+cs.CRITICAL_AREA_APPROACH_Y, MovementManager.currentPosition.z-cs.CRITICAL_AREA_APPROACH_Z), True)

        #### ramp ###
        if(cs.SEARCH_RAMP):
            #safely move away from ramp
            self.mm.moveToPos(Position(MovementManager.currentPosition.x, MovementManager.currentPosition.y + 20, 100), True)
            self.mm.waitForMovementFinished()

            # mesh left side
            x_mesh_l = np.linspace(p7[0], p10[0], n_rows)
            y_mesh_l = np.linspace(p7[1], p10[1], n_rows)
            z_mesh_l = np.linspace(p7[2], p10[2], n_rows)
            #mesh center
            x_mesh_c = np.linspace(p8[0], p11[0], n_rows)
            y_mesh_c = np.linspace(p8[1], p11[1], n_rows)
            z_mesh_c = np.linspace(p8[2], p11[2], n_rows)
            #mesh right side
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

    def pickupDieFromPosition(self, pos):
        log.info("die position: {}".format(pos))
        self.mm.setFeedratePercentage(cs.FR_DEFAULT)
        self.mm.moveToPos(cs.BEFORE_PICKUP_POSITION, True)
        self.mm.waitForMovementFinished()

        pickupPos = self.relativeBedCoordinatesToPosition(pos.x, pos.y)
        log.info("pickupPos: {}".format(pickupPos))
        #move to pick-up position
        if pickupPos.y < cs.RAMP_CRITICAL_Y:
            self.mm.moveCloseToRamp(pickupPos,segmented=True)
        else:
            self.mm.moveToPos(pickupPos, True)
        self.mm.waitForMovementFinished()
        time.sleep(cs.WAIT_ON_PICKUP_POS)
        #move away from pick-up position
        if pickupPos.y < cs.RAMP_CRITICAL_Y:
            self.mm.moveCloseToRamp(cs.AFTER_PICKUP_POSITION,segmented=True,moveto=False)
        else:
            self.mm.moveToPos(cs.AFTER_PICKUP_POSITION, True)
        self.mm.waitForMovementFinished()

    def takePicture(self, cam=None):
        if cam is None:
            cam = Camera()
        self.mm.setTopLed(cs.LED_TOP_BRIGHTNESS)
        image = cam.takePicture()
        self.dr.writeImage(image, "test.jpg", directory=cs.WEB_DIRECTORY)
        self.mm.setTopLed(cs.LED_TOP_BRIGHTNESS_OFF)
        cam.close()
        return image

    '''take a picture and locate the die'''
    def findDie(self, cam=None):
        image = self.takePicture(cam)
        dieRollResult, processedImages = self.dr.getDieRollResult(image, returnOriginalImg=True)
        return dieRollResult, processedImages

    '''take a picture and locate the die while homing is performed'''
    def findDieWhileHoming(self):
        cam = Camera(doWarmup=False)
        self.mm.doHoming(mode=2)
        image = self.takePicture(cam)
        self.mm.doHoming(mode=3)
        dieRollResult, processedImages = self.dr.getDieRollResult(image, returnOriginalImg=True)
        return dieRollResult, processedImages

    def pickupDie(self, onSendResult=None, cam=None):
        dieRollResult = DieRollResult()
        if cs.USE_IMAGE_RECOGNITION:
            dieRollResult, processedImages = self.findDie(cam)
            log.info("result: {}".format(dieRollResult.result))
            if cs.STORE_IMAGES:
                directory = "found" if dieRollResult.found else "fail"
                self.dr.writeImage(processedImages[0], directory=directory)
                self.dr.writeImage(processedImages[0], directory=cs.WEB_DIRECTORY, fileName='current_view.jpg')
                self.dr.writeRGBArray(processedImages[0], directory=directory)

        if dieRollResult.found:
            log.info("dieRollResult: {}".format(dieRollResult))
            if cs.SHOW_DIE_RESULT_WITH_LEDS:
                lm = LedManager()
                lm.showResult(dieRollResult.result)
            if onSendResult is not None:
                onSendResult(dieRollResult)
            self.pickupDieFromPosition(dieRollResult.position)
        else:
            log.info('Die not found, now searching...')
            self.searchForDie()
        return dieRollResult

    def getDropoffPosition(self, pos, stage=1):
        if stage == 1:
            p = Position(pos[0], pos[1] + cs.DROPOFF_ADVANCE_OFFSET_Y, pos[2] + cs.DROPOFF_ADVANCE_OFFSET_Z)
        elif stage == 2:
            p = Position(pos[0], pos[1] + cs.DROPOFF_ADVANCE_OFFSET_Y2, pos[2] + cs.DROPOFF_ADVANCE_OFFSET_Z2)
        return p

    def moveToDropoffPosition(self, dropoffPos, speedupFactor1=1, speedupFactor2=1):
        self.mm.setFeedratePercentage(cs.FR_DEFAULT)
        if not isinstance(dropoffPos, Position):
            dropoffPos = Position(dropoffPos[0], dropoffPos[1], dropoffPos[2])
        dropoffAdvancePos = self.getDropoffPosition(dropoffPos, stage=1)
        dropoffAdvancePos2 = self.getDropoffPosition(dropoffPos, stage=2)
        self.mm.moveToPos(dropoffAdvancePos, True)
        self.mm.setFeedratePercentage(cs.FR_DROPOFF_ADVANCE * speedupFactor1)
        self.mm.moveToPos(dropoffAdvancePos2, True)
        self.mm.setFeedratePercentage(cs.FR_DROPOFF_ADVANCE_SLOW * speedupFactor2)
        self.mm.moveToPos(dropoffPos, True)
        self.mm.waitForMovementFinished()
        self.mm.setFeedratePercentage(cs.FR_DEFAULT)

    def run(self, lastPickupX, onSendResult=None):
        # move to dropoff position
        dropoffPos = cs.MESH_MAGNET[1, :]
        px = np.clip(1 - lastPickupX / cs.LX, 0.0, 1.0)
        if (px < 0.5 and cs.USE_MAGNET_BETWEEN_P0P1):
            dropoffPos = 2 * px * cs.MESH_MAGNET[1, :] + (1 - 2 * px) * cs.MESH_MAGNET[0, :]
        if (px < 0.5 and (not cs.USE_MAGNET_BETWEEN_P0P1)):
            px=1-px
        if (px >= 0.5 and cs.USE_MAGNET_BETWEEN_P2P3):
            dropoffPos = 2 * (px - 0.5) * cs.MESH_MAGNET[3, :] + 2 * (1 - px) * cs.MESH_MAGNET[2, :]
        if (px>=0.5 and (not cs.USE_MAGNET_BETWEEN_P2P3)):
            px=1-px
            dropoffPos = 2 * px * cs.MESH_MAGNET[1, :] + (1 - 2 * px) * cs.MESH_MAGNET[0, :]

        #dropoffPos = cs.MESH_MAGNET[2, :]

        #dropoffPos = (cs.MESH_MAGNET[3, :] +  cs.MESH_MAGNET[2, :]) / 2.0

        #dropoffPos = cs.MESH_MAGNET[1, :]

        #dropoffPos = (cs.MESH_MAGNET[1, :] + cs.MESH_MAGNET[0, :]) / 2.0

        import random
        random.seed(time.time())
        index = random.randint(0, 3)
        dropoffPos = cs.MESH_MAGNET[index, :]

        self.moveToDropoffPosition(dropoffPos)

        #TODO: why is this not working?
        #cam = Camera(doWarmup=False)

        # roll die
        time.sleep(cs.WAIT_BEFORE_ROLL_TIME)
        self.mm.rollDie()
        time.sleep(cs.DIE_ROLL_TIME / 2.0)
        self.mm.setFeedratePercentage(cs.FR_DEFAULT)
        self.mm.moveToPos(cs.CENTER_TOP, True)
        time.sleep(cs.DIE_ROLL_TIME / 2.0)

        # pickup die
        dieRollResult = self.pickupDie(onSendResult)
        #cam.close()

        return dieRollResult

    def sleepUntilTimestamp(self, step, timestamps):
        sleepFor = timestamps[step] - time.time()
        print("sleep:", sleepFor)
        if sleepFor > 0:
            time.sleep(sleepFor)

    def doTestPerformance(self, startTime):
        log.info("start performance")
        startTimestamp = datetime.timestamp(startTime)
        timings = np.cumsum([0, 2, 6.5, 3, 20, 2])
        timestamps = [t + startTimestamp for t in timings]
        log.info(timestamps)
        lm = LedManager()

        step = 0
        self.sleepUntilTimestamp(step, timestamps)
        for i in range(15):
            lm.setLeds(range(0, i * 5), 255, 255, 255)
            time.sleep(0.05)
            lm.clear()
            time.sleep(0.05)

        step += 1
        self.sleepUntilTimestamp(step, timestamps)
        for i in range(10):
            lm.setLeds(range(0, i*5), i*10, i*3, i)
            time.sleep(0.5)

        step += 1
        self.sleepUntilTimestamp(step, timestamps)
        self.mm.moveToPos(cs.BEFORE_PICKUP_POSITION)

        step += 1
        self.sleepUntilTimestamp(step, timestamps)
        self.searchForDie()

        step += 1
        self.sleepUntilTimestamp(step, timestamps)
        self.mm.moveToPos(cs.BEFORE_PICKUP_POSITION)

    def doDieRollAndPickupPerformance(self, startTime):
        log.info("preparing for performance...")
        self.pickupDie()
        lm = LedManager()
        lm.clear()
        self.mm.setFeedratePercentage(cs.FR_SLOW_MOVE)
        #TODO: check if USE_MAGNET_BETWEEN_P0P1=True, otherwise use left side
        dropoffPos = cs.MESH_MAGNET[2]
        dropoffAdvancePos = Position(dropoffPos[0], dropoffPos[1] + cs.DROPOFF_ADVANCE_OFFSET_Y, dropoffPos[2] + cs.DROPOFF_ADVANCE_OFFSET_Z)
        self.mm.moveToPos(dropoffAdvancePos)
        fr_factor = 2
        fr_default_old = cs.FR_DEFAULT
        cs.FR_DEFAULT = cs.FR_DEFAULT * fr_factor
        log.info("in starting position...")
        log.info("waiting for performance to start...")
        startTimestamp = datetime.timestamp(startTime)
        timings = np.cumsum([0,
                             0.25, # turn on leds
                             6.0, # move to dropoff position
                             2,   # roll die and mvoe to cs.CENTER_TOP
                             0.9+4.2, # take picture
                             0.3, # move to cs.BEFORE_PICKUP_POSITION
                             5.1, # find die on image
                             4.9  # pickup die
                            ])    # move to starting position (dropoff advance position)
        timestamps = [t + startTimestamp for t in timings]
        log.info(timestamps)

        step = 0
        self.sleepUntilTimestamp(step, timestamps)
        #cam = Camera(doWarmup=False)
        lm.setAllLeds()

        step += 1
        self.sleepUntilTimestamp(step, timestamps)
        self.moveToDropoffPosition(cs.MESH_MAGNET[2], speedupFactor1=1.5, speedupFactor2=1)
        #self.moveToDropoffPosition(cs.MESH_MAGNET[2], speedupFactor1=3, speedupFactor2=3)

        step += 1
        self.sleepUntilTimestamp(step, timestamps)
        self.mm.setFeedratePercentage(cs.FR_DEFAULT)
        self.mm.rollDie()
        time.sleep(0.4)
        self.mm.moveToPos(cs.CENTER_TOP, True)

        step += 1
        self.sleepUntilTimestamp(step, timestamps)
        #image = self.takePicture(cam)
        image = self.takePicture()

        step += 1
        self.sleepUntilTimestamp(step, timestamps)
        self.mm.moveToPos(cs.BEFORE_PICKUP_POSITION)

        step += 1
        self.sleepUntilTimestamp(step, timestamps)
        dieRollResult, _ = self.dr.getDieRollResult(image, returnOriginalImg=True)

        step += 1
        self.sleepUntilTimestamp(step, timestamps)
        if dieRollResult.found:
            self.pickupDieFromPosition(dieRollResult.position)
        else:
            self.searchForDie()

        step += 1
        self.sleepUntilTimestamp(step, timestamps)
        self.mm.moveToPos(dropoffAdvancePos, True)
        lm.clear()

        cs.FR_DEFAULT = fr_default_old

    def doPositionTestWithTiming(self, startTime, clientIdentity, x, y ,z):
        log.info("preparing for performance...")
        lm = LedManager()
        lm.clear()
        self.mm.setTopLed(cs.LED_TOP_BRIGHTNESS_OFF)
        log.info("waiting for performance to start...")
        startTimestamp = datetime.timestamp(startTime)
        timings = np.cumsum([clientIdentity["Position"]*0.2, # wait for position to be next
                             27 * 0.2 + 1])  # light up
        timestamps = [t + startTimestamp for t in timings]
        log.info(timestamps)

        step = 0
        self.sleepUntilTimestamp(step, timestamps)
        p = int(clientIdentity["Position"])
        f = x + y + z
        r = cs.LED_STRIP_DEFAULT_COLOR[0] + 10 * f
        g = cs.LED_STRIP_DEFAULT_COLOR[1] - 8 * f
        b = cs.LED_STRIP_DEFAULT_COLOR[2]
        lm.setAllLeds(r=r, g=g, b=b)

        step += 1
        self.sleepUntilTimestamp(step, timestamps)
        lm.clear()