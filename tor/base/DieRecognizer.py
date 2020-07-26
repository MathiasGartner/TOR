import cv2
from datetime import datetime
import math
import numpy as np
import os

from tor.base.utils.Point2D import Point2D
import tor.client.ClientSettings as cs

class DieRecognizer:
    def __init__(self):
        self.warpMatrix, self.warpWidth, self.warpHeight = self.createWarpMatrix(cs.IMG_TL, cs.IMG_BL, cs.IMG_TR, cs.IMG_BR)
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

    def createWarpMatrix(self, tl, bl, tr, br):
        w = max((tr[0] - tl[0]), (br[0] - bl[0]))
        h = max((bl[1] - tl[1]), (br[1] - tr[1]))
        #w = int(w / 2)
        #h = int(h / 2)
        #print("warp matrix with w:", w, "h:", h)
        src = np.array([tl, bl, tr, br], dtype="float32")
        dst = np.array([[0, 0],
                        [0, h - 1],
                        [w - 1, 0],
                        [w - 1, h - 1]], dtype="float32")
        mat = cv2.getPerspectiveTransform(src, dst)
        return mat, w, h

    def readDummyImage(self, imNr=1, path=r"D:\Dropbox\Uni\AEC\Elektronik\Raspi\2_2_neue Kamera testen\test{:03d}.jpg"):
        #image = cv2.imread(r"D:\Dropbox\Uni\AEC\Elektronik\Raspi\2_2_neue Kamera testen\test{:03d}.jpg".format(imNr))
        imgPath = path.format(imNr)
        image = cv2.imread(imgPath)
        if image is None:
            raise Exception("Could not open image: ", imgPath)
        return image

    def readDummyRGBArray(self, imNr=1, path=r"D:\Dropbox\Uni\AEC\Elektronik\Raspi\2_2_neue Kamera testen\test{:03d}.jpg"):
        imgPath = path.format(imNr)
        image = np.load(imgPath)
        if image is None:
            raise Exception("Could not open image: ", imgPath)
        return image

    def writeImage(self, im, fileName="", directory=""):
        if fileName == "":
            fileName = "run_{}.jpg".format(datetime.now().strftime("%Y%m%d%H%M%S"))
        if directory != "":
            fileName = os.path.join(directory, fileName)
        cv2.imwrite(fileName, im)

    def writeRGBArray(self, im, fileName="", directory=""):
        if fileName == "":
            fileName = "run_{}.npy".format(datetime.now().strftime("%Y%m%d%H%M%S"))
        if directory != "":
            fileName = os.path.join(directory, fileName)
        np.save(fileName, im)

    def markCropLines(self, im, tl, br, isGray=False):
        if not isGray:
            im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
        im = cv2.rectangle(im, tuple(tl), tuple(br), (0, 0, 255), thickness=1)
        return im

    def markLines(self, im, lines, isGray=False):
        if not isGray:
            im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
        for l in lines:
            im = cv2.line(im, tuple(l[0]), tuple(l[1]), (0, 0, 255), thickness=1)
        return im

    def cropImage(self, image, tl = cs.IMG_TL, br = cs.IMG_BR):
        cropped = image[tl[1]:br[1], tl[0]:br[0]]
        return cropped

    def warpImage(self, image):
        warped = cv2.warpPerspective(image, self.warpMatrix, (self.warpWidth, self.warpHeight))
        return warped

    def transformImage(self, image):
        if cs.IMG_USE_WARPING:
            return self.warpImage(image)
        else:
            return self.cropImage(image)

    def markDieOnImage(self, im, keypoints, isGray=False):
        if isGray:
            im_color = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
        else:
            im_color = im.copy()
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

    def getDiePosition(self, im, withUI = False, returnOriginalImg=True, alreadyCropped=False, alreadyGray=False):
        if not alreadyCropped:
            im = self.cropToSearchableArea(im)
        im_original = im
        if not alreadyGray:
            im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

        #Blur the image
        blurSize = 13
        #im = cv2.blur(im, (blurSize, blurSize))
        im = cv2.medianBlur(im, blurSize)
        #im = cv2.GaussianBlur(im, (blurSize, blurSize), 13, 13)
        #im = cv2.bilateralFilter(im, blurSize, blurSize / 2, blurSize / 2)

        threshold_min = 70
        retVal, im = cv2.threshold(im, threshold_min, 255, cv2.THRESH_BINARY)

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

        diePositionRelative = Point2D(-1, -1)
        if len(blobs) > 0:
            if len(blobs) > 6:
                #TODO: choose the correct ones
                found = False
                result = 0
            else:
                #TODO: check if the detected blobs correspond to the face of a die
                #      eg. distance between blobs, arrangement, ...
                meanX = np.mean([blob.pt[0] for blob in blobs])
                meanY = np.mean([blob.pt[1] for blob in blobs])

                offset = 60
                diePositionPX = Point2D(meanX, meanY)
                diePositionRelative.x = (diePositionPX.x - offset) / (im.shape[1] - 2 * offset)
                diePositionRelative.y = 1.0 - (diePositionPX.y - offset) / (im.shape[0] - 2 * offset)
                print("diePositionPX:", diePositionPX)
                print("diePositionRelative:", diePositionRelative)
                found = True
                result = len(blobs)
        else:
            found = False
            result = 0
        return (found, diePositionRelative, result, (im_original, im_with_blobs))

    def getDieResult(self):
        #TODO: not implemented yet
        return 0

    def getDieResultWithExtensiveProcessing(self):
        #TODO: not implemented yet
        return 0

    def checkIfDiePickedUp(self):
        #TODO: compare to previous image and check if die is now missing
        return True