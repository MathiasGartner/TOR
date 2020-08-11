
import argparse
import cv2
import numpy as np
import time

import tor.client.ClientSettings as cs
from tor.base.DieRecognizer import DieRecognizer
from tor.client.Camera import Camera
from tor.client.MovementManager import MovementManager
from tor.client.MovementRoutines import MovementRoutines
from tor.client.LedManager import LedManager

parser = argparse.ArgumentParser()
parser.add_argument("-t", dest="theater", action="store_true")
parser.add_argument("-all", dest="all", action="store_true")
args = parser.parse_args()

mm = MovementManager()
lm = LedManager()
mr = MovementRoutines()

print("TOR-Marlin v{} installed, v{} required.".format(mm.torMarlinVersion, cs.TOR_MARLIN_VERSION))
if not mm.hasCorrectVersion:
    exit(0)

print("Test top led ...")
for i in range(0, 256, 5):
    mm.setTopLed(i)
    time.sleep(0.1)
mm.setTopLed(0)

print("Test led strip ...")
lm.test()

if args.theater:
    print("Test led strip ...")
    lm.testTheaterChaseRainbow()

lm.clear()

print("Test homing ...")
mm.doHoming()
time.sleep(2)

print("Move to center ...")
mm.moveToPos(cs.BEFORE_PICKUP_POSITION)
mm.waitForMovementFinished()

print("Test die roll ...")
dropoffPos = np.array((90, 7, 13))
mr.moveToDropoffPosition(dropoffPos)
time.sleep(cs.WAIT_BEFORE_ROLL_TIME)
mm.setFeedratePercentage(cs.FR_FAST_MOVES)
mm.rollDie()

print("Move to center ...")
mm.moveToPos(cs.BEFORE_PICKUP_POSITION, True)
mm.waitForMovementFinished()

print("Test camera ...")
cam = Camera()
dr = DieRecognizer()
image = cam.takePicture()
cam.close()
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
image = dr.transformImage(image)
dr.writeImage(image, "current_view.jpg", directory=cs.WEB_DIRECTORY)

print("Pickup die ...")
cs.STORE_IMAGES = True
cs.SHOW_DIE_RESULT_WITH_LEDS = True
#mr.pickupDie()
mr.searchForDie()
lm.clear()

print("Done!")