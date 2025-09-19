import cv2
import matplotlib.pyplot as plt

from tor.base.DieRecognizer import DieRecognizer

imageDirectory = "/home/tor/TORPictures/dice_20220914/fail"
imageDirectoryFound = "/home/tor/TORPictures/dice_20220914/found"

def readImages(filenames):
    ims = []
    for filename in filenames:
        im = cv2.imread(filename)
        ims.append(im)
    return ims

dr = DieRecognizer()

filenames = []
filenames = [imageDirectory + "/marked_id=3_20220914051554.png"]
filenames = [imageDirectoryFound + "/marked_id=10_20220914093552.jpg"]
images = readImages(filenames)
for im in images:
    dieRollResult, processedImages = dr.getDieRollResult(im, withUI = True, returnOriginalImg=True, alreadyCropped=True, alreadyGray=False, markDie=True)

    f, axarr = plt.subplots(1,2)
    axarr[0,0].imshow(processedImages[0])
    axarr[0,1].imshow(processedImages[1])
    f.show()

