import cv2
from datetime import datetime
import math
import numpy as np

from tor.base.utils.Point2D import Point2D
import tor.client.ClientSettings as cs

class DieRecognizer:
    def __init__(self):
        self.blobParams = cv2.SimpleBlobDetector_Params()
        self.blobParams.filterByColor = True
        self.blobParams.blobColor = 0
        self.blobParams.filterByArea = True
        self.blobParams.minArea = (cs.BLOB_MIN_DIAMETER / 2) ** 2 * math.pi
        self.blobParams.maxArea = (cs.BLOB_MAX_DIAMETER / 2) ** 2 * math.pi
        self.blobParams.filterByCircularity = True
        self.blobParams.minCircularity = 0.8
        self.blobParams.maxCircularity = 1.1
        self.blobParams.filterByConvexity = True
        self.blobParams.minConvexity = 0.9
        self.blobParams.maxConvexity = 1.0
        self.blobParams.filterByInertia = True
        self.blobParams.minInertiaRatio = 0.5
        self.blobParams.maxInertiaRatio = 1.0
        self.blobDetector = cv2.SimpleBlobDetector_create(self.blobParams)

    def readDummyImage(self, imNr=1, path=r"D:\Dropbox\Uni\AEC\Elektronik\Raspi\2_2_neue Kamera testen\test{:03d}.jpg"):
        #image = cv2.imread(r"D:\Dropbox\Uni\AEC\Elektronik\Raspi\2_2_neue Kamera testen\test{:03d}.jpg".format(imNr))
        #range 0 - 16
        imgPath = path.format(imNr)
        image = cv2.imread(imgPath)
        if image is None:
            raise Exception("Could not open image: ", imgPath)
        return image

    def writeImage(self, im):
        cv2.imwrite("run_{}.jpg".format(datetime.now().strftime("%Y%m%d%H%M%S")), im)
        pass

    def cropToSearchableArea(self, im):
        cropped = im[cs.IMAGE_CROP_Y_TOP:(im.shape[0] - cs.IMAGE_CROP_Y_BOTTOM), cs.IMAGE_CROP_X_LEFT:(im.shape[1] - cs.IMAGE_CROP_X_RIGHT)]
        return cropped

    def px_to_mm(self, px, pxpmm=1):
        if type(px) == Point2D:
            mm = Point2D(self.px_to_mm(px.x, cs.AREA_PX_PER_MM_X), self.px_to_mm(px.y, cs.AREA_PX_PER_MM_Y))
        else:
            mm = px / pxpmm
        return mm

    def markDieOnImage(self, im, keypoints):
        im_color = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
        if len(keypoints) > 0:
            padding = 50
            minX = max(int(np.min([k.pt[0] for k in keypoints])) - padding, 0)
            maxX = min(int(np.max([k.pt[0] for k in keypoints])) + padding, im_color.shape[1])
            minY = max(int(np.min([k.pt[1] for k in keypoints])) - padding, 0)
            maxY = min(int(np.max([k.pt[1] for k in keypoints])) + padding, im_color.shape[0])
            for p in keypoints:
                x = np.int(p.pt[0])
                y = np.int(p.pt[1])
                size = np.int(p.size)
                im_color = cv2.circle(im_color, (x, y), int(size/2), (0, 0, 255), thickness=3)
            im_color = cv2.rectangle(im_color, (minX, minY), (maxX, maxY), (0, 0, 255), thickness=10)
        return im_color

    def getDiePosition(self, im, withUI = False, returnOriginalImg=True):
        im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        im = self.cropToSearchableArea(im)
        im_original = im

        #Blur the image
        blurSize = 13
        #im = cv2.blur(im, (blurSize, blurSize))
        im = cv2.medianBlur(im, blurSize)
        #im = cv2.GaussianBlur(im, (blurSize, blurSize), 13, 13)
        #im = cv2.bilateralFilter(im, blurSize, blurSize / 2, blurSize / 2)

        retVal, im = cv2.threshold(im, 45, 255, cv2.THRESH_BINARY)

        blobs = self.blobDetector.detect(im)

        #im_with_blobs = cv2.drawKeypoints(im, blobs, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        if returnOriginalImg:
            im_with_blobs = self.markDieOnImage(im_original, blobs)
        else:
            im_with_blobs = self.markDieOnImage(im, blobs)

        if withUI:
            windowX = int(im.shape[1]/3)
            windowY = int(im.shape[0]/3)
            cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Original", windowX, windowY)
            cv2.namedWindow("Blobs", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Blobs", windowX, windowY)

            cv2.imshow("Original", im_original)
            cv2.imshow("Blobs", im_with_blobs)

            cv2.waitKey(10000)
            cv2.destroyAllWindows()

        if len(blobs) > 0:
            if len(blobs) > 6:
                #TODO: choose the correct ones
                found = False
                diePositionPX = Point2D(-1, -1)
                diePositionMM = Point2D(-1, -1)
                result = 0
            else:
                meanX = np.mean([blob.pt[0] for blob in blobs])
                meanY = np.mean([blob.pt[1] for blob in blobs])

                diePositionPX = Point2D(meanX, meanY)
                diePositionMM = self.px_to_mm(diePositionPX)
                diePositionMM.y = cs.LY - diePositionMM.y + 15 #TODO: check mapping of y value from pixel to mm
                found = True
                result = min(len(blobs), 6)
        else:
            found = False
            diePositionPX = Point2D(-1, -1)
            diePositionMM = Point2D(-1, -1)
            result = 0
        return (found, diePositionMM, result, (im_original, im_with_blobs))

    def getDieResult(self):
        #TODO: not implemented yet
        return 0

    def getDieResultWithExtensiveProcessing(self):
        #TODO: not implemented yet
        return 0

    def checkIfDiePickedUp(self):
        #TODO: compare to previous image and check if die is now missing
        return True