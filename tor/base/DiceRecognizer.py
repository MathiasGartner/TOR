import cv2
import numpy as np

class DiceRecognizer:
    def __init__(self):
        self.blobParams = cv2.SimpleBlobDetector_Params()
        self.blobParams.blobColor = 0
        self.blobParams.minArea = 500
        self.blobDetector = cv2.SimpleBlobDetector_create(self.blobParams)

    def readDummyImage(self):
        #image = cv2.imread(r"D:\Dropbox\Uni\AEC\Elektronik\Raspi\2_2_neue Kamera testen\test1.jpg")
        image = cv2.imread(r"D:\Dropbox\Uni\AEC\Elektronik\Raspi\2_2_neue Kamera testen\test2.jpg")
        return image

    def getDiePosition(self, im, withUI = False):
        im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        blobs = self.blobDetector.detect(im)

        meanX = np.mean([blob.pt[0] for blob in blobs])
        meanY = np.mean([blob.pt[1] for blob in blobs])
        print(meanX, meanY)

        im_with_blobs = cv2.drawKeypoints(im, blobs, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        if withUI:
            cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Original", 800, 600)
            cv2.namedWindow("Blobs", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Blobs", 800, 600)

            cv2.imshow("Original", im)
            cv2.imshow("Blobs", im_with_blobs)

            cv2.waitKey(5000)
            cv2.destroyAllWindows()

        dieX = meanX
        dieY = meanY
        found = True
        result = min(len(blobs), 6)
        return (found, dieX, dieY, result)

    def checkIfDiePickedUp(self):
        #TODO: compare to previous image and check if die is now missing
        pass