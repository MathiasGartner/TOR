import logging
log = logging.getLogger(__name__)

import cv2
from datetime import datetime
import os
import time

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def clamp255(n):
    return clamp(n, 0, 255)

def sleepUntilTimestampIndex(step, timestamps):
    sleepFor = timestamps[step] - time.time()
    log.info("sleep: {}".format(sleepFor))
    if sleepFor > 0:
        time.sleep(sleepFor)

def sleepUntilTimestamp(timestamp):
    sleepUntilTimestampIndex(0, [timestamp])

def createDirectory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def getFilenameTimestamp():
    return datetime.now().strftime("%Y%m%d%H%M%S")

def getFilenameTimestampDay():
    return datetime.now().strftime("%Y%m%d")

def writeImage(im, fileName="", directory="", doCreateDirectory=False):
    if fileName == "":
        fileName = "run_{}.jpg".format(datetime.now().strftime("%Y%m%d%H%M%S"))
    if directory != "":
        if doCreateDirectory:
            createDirectory(directory)
        fileName = os.path.join(directory, fileName)
    cv2.imwrite(fileName, im)