#!/usr/bin/env python3

import random
import sys
import time

from tor.base.DieRecognizer import DieRecognizer
import tor.client.ClientSettings as cs
from tor.client.Cords import Cords
from tor.client.LedManager import LedManager
from tor.client.MovementManager import MovementManager
from tor.client.Position import Position

mode = 4
if len(sys.argv) > 1:
    mode=int(sys.argv[1])
print("mode: ", mode)

try:
    if mode == 17:
        from tor.client.Camera import Camera
    if mode != 17 and mode != 15:
        print("init board...")
        mm = MovementManager()
        mm.initBoard()
        time.sleep(0.5)
    else:
        mm = None
except:
    mm = None
    print("ERROR: could not connect to SKR board.")


if mode == 0:
    diePosition = Position(100, 30, 210)
    mm.moveToPos(cs.HOME_POSITION)
    mm.moveToPos(diePosition)
    mm.moveToPos(cs.HOME_POSITION)

    dieX = 120
    dieY = 160
    mm.moveToXYPosDie(dieX, dieY)
    mm.waitForMovementFinished(0.5)
    mm.moveToXPosRamp(dieX)

elif mode == 1: #move to x y and pick up die
    dieX = int(sys.argv[2])
    dieY = int(sys.argv[3])
    mm.moveToXYPosDie(dieX, dieY)
    mm.waitForMovementFinished(0.5)
    mm.moveToXPosRamp(dieX)

elif mode == 2: #move to x y z
    pos = Position(float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]))
    mm.moveToPos(pos)

elif mode == 3: #move to all corners
    mm.moveToAllCorners()

elif mode == 4: #search for die
    mm.searchForDie()
    mm.moveToXPosRamp(cs.LX/2)

elif mode == 5: #move to x y z segmented
    pos = Position(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    mm.moveToPosSegmented(pos)

elif mode == 6: #home to Z anchor
    mm.doHoming()

elif mode == 7: #test dropoff
    while (True):
        mm.doHoming()
        mm.waitForMovementFinished(0.5)
        mm.moveToPos(cs.CENTER_TOP)
        mm.waitForMovementFinished(0.5)
        mm.moveToPos(cs.DROPOFF_ADVANCE_POSITION)
        mm.waitForMovementFinished(0.5)
        mm.moveToPos(cs.DROPOFF_POSITION, segmented=True)
        mm.waitForMovementFinished(2)
        mm.moveToPos(cs.DROPOFF_ADVANCE_POSITION)
        mm.waitForMovementFinished(0.5)

elif mode == 8:  # led test
    lm = LedManager()
    lm.test()
    for i in range(1, 7):
        lm.showResult(i)
        time.sleep(1)
    for i in [random.randint(1, 6) for x in range(1, 4)]:
        lm.showResult(i)
        time.sleep(1)
    lm.clear()

elif mode == 9: # take picture and search dice dots
    from tor.base.DieRecognizer import DieRecognizer
    if cs.ON_RASPI:
        from tor.client.Camera import Camera
    #lm = LedManager()
    dr = DieRecognizer()
    if cs.ON_RASPI:
        cam = Camera()
        image = cam.takePicture()
    else:
        image = dr.readDummyImage()
    print("analyze picture...")
    found, diePosition, result, processedImages = dr.getDiePosition(image, returnOriginalImg=True)
    print("write image...")
    dr.writeImage(processedImages[1])
    print("result:", result)
    #lm.showResult(result)

elif mode == 10: #leds
    lm = LedManager()
    lm.testRightLeftBack()

elif mode == 11: # clear leds
    lm = LedManager()
    lm.clear()

elif mode == 12: # leds
    lm = LedManager()
    for i in range(0, cs.LED_COUNT):
        lm.strip.setPixelColor(i, lm.W)
    lm.strip.show()

elif mode == 13: # test magnet pulse
    mm.pulseMagnet()

elif mode == 14: #test top led
    for i in range(10):
        mm.setLed(int(sys.argv[2]))
        time.sleep(0.3)
        mm.setLed(0)
        time.sleep(0.3)

elif mode == 15: #set led strip segments
    r = int(sys.argv[2])
    g = int(sys.argv[3])
    b = int(sys.argv[4])
    segment = sys.argv[5]
    brightness = int(sys.argv[6])

    lm = LedManager(brightness)
    if "L" in segment:
        leds = cs.LEDS_LEFT
        lm.setLeds(leds, r, g, b)
    if "R" in segment:
        leds = cs.LEDS_RIGHT
        lm.setLeds(leds, r, g, b)
    if "B" in segment:
        leds = cs.LEDS_BACK
        lm.setLeds(leds, r, g, b)
    if "A" in segment:
        leds = cs.LEDS_BEFORE
        lm.setLeds(leds, r, g, b)
    if "Z" in segment:
        leds = cs.LEDS_AFTER
        lm.setLeds(leds, r, g, b)

elif mode == 16: # move forever
    mm.setCurrentPosition(Cords([0, 0, 0, 0]))
    while True:
        length = 50
        mm.moveToCords(Cords([length, length, length, length]))
        mm.waitForMovementFinished(0.5)
        mm.moveToCords(Cords([0, 0, 0, 0]))
        mm.waitForMovementFinished(0.5)

elif mode == 17: # take pictures forever
    i = 0
    cam = Camera()
    dr = DieRecognizer()
    while True:
        image = cam.takePicture()
        print("analyze picture...")
        found, diePosition, result, processedImages = dr.getDiePosition(image, returnOriginalImg=True)
        if i == 100:
            i = 0
            dr.writeImage(processedImages[1])
        i += 1

if mm is not None:
    mm.waitForMovementFinished(2)
    #mm.moveHome()


