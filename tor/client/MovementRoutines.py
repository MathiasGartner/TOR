import numpy as np

from tor.base.DieRecognizer import DieRecognizer
from tor.client import ClientSettings as cs
from tor.client.Camera import Camera
from tor.client.LedManager import LedManager
from tor.client.MovementManager import MovementManager
from tor.client.Position import Position

class MovementRoutines:
    def __init__(self):
        self.mm = MovementManager()
        self.dr = DieRecognizer()

    def loadPoints(self):
        return np.concatenate((cs.MESH_BED, cs.MESH_RAMP))

    def relativeBedCoordinatesToPosition(self, px, py):
        p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12 = self.loadPoints()
        if (px < 0 or px > 1 or py < -0.1 or py > 1):
            print("Out of range!:", px, py)
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

    def pickupDie(self):
        found = False
        result = -1
        diePosition = None
        if cs.USE_IMAGE_RECOGNITION:
            cam = Camera()
            self.mm.setTopLed(cs.LED_TOP_BRIGHTNESS)
            image = cam.takePicture()
            self.mm.setTopLed(cs.LED_TOP_BRIGHTNESS_OFF)
            cam.close()

            found, diePosition, result, processedImages = self.dr.getDiePosition(image, returnOriginalImg=True)
            print("result:", result)
            if cs.STORE_IMAGES:
                directory = "found" if found else "fail"
                self.dr.writeImage(processedImages[0], directory=directory)
                self.dr.writeRGBArray(processedImages[0], directory=directory)

        if found:
            if cs.SHOW_DIE_RESULT_WITH_LEDS:
                lm = LedManager()
                lm.showResult(result)
            print("die position:", diePosition)
            self.mm.setFeedratePercentage(cs.FR_DEFAULT)
            self.mm.moveToPos(cs.BEFORE_PICKUP_POSITION, True)
            self.mm.waitForMovementFinished()

            pickupPos = self.relativeBedCoordinatesToPosition(diePosition.x,diePosition.y)
            print("pickupPos:", pickupPos)
            self.mm.moveToPos(pickupPos, True)
            self.mm.waitForMovementFinished()
            self.mm.moveToPos(cs.AFTER_PICKUP_POSITION, True)
            self.mm.waitForMovementFinished()
        else:
            print('Die not found, now searching...')
            self.searchForDie()
        return found, result, diePosition

    def run(self):
        pass