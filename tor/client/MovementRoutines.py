import logging
log = logging.getLogger(__name__)

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
        oldFeedratePercentage = self.mm.feedratePercentage
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
                self.mm.moveToPos(Position(x_mesh_c[i], y_mesh_c[i], z_mesh_c[i]), True)
                #self.mm.waitForMovementFinished()
                self.mm.moveToPos(Position(x_mesh_r[i], y_mesh_r[i], z_mesh_r[i]), True)
                self.mm.waitForMovementFinished()
            else:
                self.mm.moveToPos(Position(x_mesh_r[i], y_mesh_r[i], z_mesh_r[i]), True)
                #self.mm.waitForMovementFinished()
                self.mm.moveToPos(Position(x_mesh_c[i], y_mesh_c[i], z_mesh_c[i]), True)
                #self.mm.waitForMovementFinished()
                self.mm.moveToPos(Position(x_mesh_l[i], y_mesh_l[i], z_mesh_l[i]), True)
                self.mm.waitForMovementFinished()

        #### ramp ###
        if(cs.SEARCH_RAMP):
            #safely move away from ramp
            self.mm.moveToPos(Position(self.mm.currentPosition.x, self.mm.currentPosition.y + 20, 100), True)
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

        self.mm.setFeedratePercentage(oldFeedratePercentage)
        self.mm.moveToPos(cs.AFTER_PICKUP_POSITION, True)
        self.mm.waitForMovementFinished()

    def pickupDieFromPosition(self, pos):
        log.info("die position: {}".format(pos))
        self.mm.setFeedratePercentage(cs.FR_DEFAULT)
        self.mm.moveToPos(cs.BEFORE_PICKUP_POSITION, True)
        self.mm.waitForMovementFinished()

        pickupPos = self.relativeBedCoordinatesToPosition(pos.x, pos.y)
        log.info("pickupPos: {}".format(pickupPos))
        self.mm.moveToPos(pickupPos, True)
        self.mm.waitForMovementFinished()
        time.sleep(cs.WAIT_ON_PICKUP_POS)
        self.mm.moveToPos(cs.AFTER_PICKUP_POSITION, True)
        self.mm.waitForMovementFinished()

    def findDie(self):
        cam = Camera()
        self.mm.setTopLed(cs.LED_TOP_BRIGHTNESS)
        image = cam.takePicture()
        self.mm.setTopLed(cs.LED_TOP_BRIGHTNESS_OFF)
        cam.close()
        dieRollResult, processedImages = self.dr.getDieRollResult(image, returnOriginalImg=True)
        return dieRollResult, processedImages

    def pickupDie(self):
        dieRollResult = DieRollResult()
        if cs.USE_IMAGE_RECOGNITION:
            dieRollResult, processedImages = self.findDie()
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
            #TODO: send dieRollResult here
            self.pickupDieFromPosition(dieRollResult.position)
        else:
            log.info('Die not found, now searching...')
            self.searchForDie()
        return dieRollResult

    def run(self, lastPickupX):
        # move to dropoff position
        dropoffPos = cs.MESH_MAGNET[1, :]
        px = np.clip(1 - lastPickupX / cs.LX, 0.0, 1.0)
        if px < 0.5:
            dropoffPos = 2 * px * cs.MESH_MAGNET[1, :] + (1 - 2 * px) * cs.MESH_MAGNET[0, :]
        else:
            dropoffPos = 2 * (px - 0.5) * cs.MESH_MAGNET[3, :] + 2 * (1 - px) * cs.MESH_MAGNET[2, :]
        self.mm.setFeedratePercentage(cs.FR_DEFAULT)
        self.mm.moveToPos(Position(dropoffPos[0], dropoffPos[1] + 20, 30), True)
        self.mm.setFeedratePercentage(cs.FR_DROPOFF_ADVANCE)
        self.mm.moveToPos(Position(dropoffPos[0], dropoffPos[1] + 10, dropoffPos[2] + 10), True)
        self.mm.setFeedratePercentage(cs.FR_DROPOFF_ADVANCE_SLOW)
        self.mm.moveToPos(Position(dropoffPos[0], dropoffPos[1], dropoffPos[2]), True)
        self.mm.waitForMovementFinished()

        # roll die
        time.sleep(cs.WAIT_BEFORE_ROLL_TIME)
        self.mm.setFeedratePercentage(cs.FR_FAST_MOVES)
        self.mm.rollDie()
        time.sleep(cs.DIE_ROLL_TIME / 2.0)
        self.mm.moveToPos(cs.CENTER_TOP, True)
        time.sleep(cs.DIE_ROLL_TIME / 2.0)

        # pickup die
        dieRollResult = self.pickupDie()

        return dieRollResult