import cv2
import math
import numpy as np

from tor.base.utils.Point2D import Point2D
import tor.client.ClientSettings as cs

class DiceRecognizer:
    def __init__(self):
        self.blobParams = cv2.SimpleBlobDetector_Params()
        self.blobParams.filterByColor = True
        self.blobParams.blobColor = 0
        self.blobParams.filterByArea = True
        self.blobParams.minArea = (20 / 2) ** 2 * math.pi
        self.blobParams.maxArea = (25 / 2) ** 2 * math.pi
        self.blobParams.filterByCircularity = True
        self.blobParams.minCircularity = 0.8
        self.blobParams.maxCircularity = 1.1
        self.blobParams.filterByConvexity = True
        self.blobParams.minConvexity = 0.9
        self.blobParams.maxConvexity = 1.0
        self.blobParams.filterByInertia = True
        self.blobParams.minInertiaRatio = 0.6
        self.blobParams.maxInertiaRatio = 1.0
        self.blobDetector = cv2.SimpleBlobDetector_create(self.blobParams)

    def readDummyImage(self):
        image = cv2.imread(r"D:\Dropbox\Uni\AEC\Elektronik\Raspi\2_2_neue Kamera testen\test.jpg")
        #image = cv2.imread(r"D:\Dropbox\Uni\AEC\Elektronik\Raspi\2_2_neue Kamera testen\test1.jpg")
        #image = cv2.imread(r"D:\Dropbox\Uni\AEC\Elektronik\Raspi\2_2_neue Kamera testen\test2.jpg")
        return image

    def cropToSearchableArea(self, im):
        cropped = im[cs.IMAGE_CROP_X_TOP:(im.shape[0] - cs.IMAGE_CROP_X_BOTTOM), cs.IMAGE_CROP_Y_LEFT:(im.shape[1] - cs.IMAGE_CROP_Y_RIGHT)]
        return cropped

    def px_to_mm(self, px, pxpmm=1):
        if type(px) == Point2D:
            mm = Point2D(self.px_to_mm(px.x, cs.AREA_PX_PER_MM_X), self.px_to_mm(px.y, cs.AREA_PX_PER_MM_Y))
        else:
            mm = px / pxpmm
        return mm

    def getDiePosition(self, im, withUI = False):
        im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        im = self.cropToSearchableArea(im)
        im_original = im

        #Blur the image
        blurSize = 21
        #im = cv2.blur(im, (blurSize, blurSize))
        im = cv2.medianBlur(im, blurSize)
        #im = cv2.GaussianBlur(im, (blurSize, blurSize), 0)
        #im = cv2.bilateralFilter(im, blurSize, blurSize / 2, blurSize / 2)

        retVal, im = cv2.threshold(im, 45, 255, cv2.THRESH_BINARY)

        blobs = self.blobDetector.detect(im)

        low = 0
        high = 40
        dots = cv2.inRange(im, low, high)

        meanX = np.mean([blob.pt[0] for blob in blobs])
        meanY = np.mean([blob.pt[1] for blob in blobs])
        print(meanX, meanY)

        if withUI:
            windowX = int(im.shape[1]/2)
            windowY = int(im.shape[0]/2)
            cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Original", windowX, windowY)
            cv2.namedWindow("Blobs", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Blobs", windowX, windowY)

            cv2.imshow("Original", im_original)

            im_with_blobs = cv2.drawKeypoints(im, blobs, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            cv2.imshow("Blobs", im_with_blobs)

            cv2.waitKey(10000)
            cv2.destroyAllWindows()

        diePositionPX = Point2D(meanX, meanY)
        diePositionMM = self.px_to_mm(diePositionPX)
        found = True
        result = min(len(blobs), 6)
        return (found, diePositionPX, diePositionMM, result)

    def checkIfDiePickedUp(self):
        #TODO: compare to previous image and check if die is now missing
        pass