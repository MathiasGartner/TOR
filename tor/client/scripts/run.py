#!/usr/bin/env python3

import random
import sys
import time

from datetime import datetime

import numpy as np

from tor.base.DieRecognizer import DieRecognizer
import tor.client.ClientSettings as cs
from tor.client.Cords import Cords
if cs.ON_RASPI:
    from tor.client.Camera import Camera
from tor.client.LedManager import LedManager
from tor.client.MovementManager import MovementManager
from tor.client.Position import Position

mode = 18
if len(sys.argv) > 1:
    mode=int(sys.argv[1])
print("mode: ", mode)

try:
    if mode == 17:
        from tor.client.Camera import Camera
    if mode == 23:
        from tor.client.ClientManager import ClientManager
        from tor.client.MovementRoutines import MovementRoutines
        cm = ClientManager()
        mr = MovementRoutines(cm)
    if mode != 17 and mode != 18 and mode != 15 and mode != 11 and mode != 12 and mode != 10:
        print("init board...")
        mm = MovementManager()
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
    mm.setFeedratePercentage(150)
    mm.moveToAllCorners(int(sys.argv[2]) == 1)

elif mode == 4: #search for die
    mm.searchForDie()
    mm.moveToXPosRamp(cs.LX/2)

elif mode == 5: #move to x y z segmented
    pos = Position(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    mm.moveToPosSegmented(pos)

elif mode == 6: #home to Z anchor
    mm.doHoming()
    print("Position after homing: {}".format(mm.currentPosition))

elif mode == 7: #test dropoff
    while (True):
        mm.doHoming()
        mm.waitForMovementFinished(0.5)
        mm.moveToPos(cs.CENTER_TOP)
        mm.waitForMovementFinished(0.5)
        mm.moveToPos(cs.DROPOFF_ADVANCE_POSITION)
        mm.waitForMovementFinished(0.5)
        mm.setFeedratePercentage(cs.FR_DROPOFF_ADVANCE)
        mm.moveToPos(cs.DROPOFF_POSITION, segmented=True)
        mm.setFeedratePercentage(cs.FR_DEFAULT)
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
        cam.close()
    else:
        image = dr.readDummyImage()
    print("analyze picture...")
    dieRollResult, processedImages = dr.getDieRollResult(image, returnOriginalImg=True)
    print("write image...")
    dr.writeImage(processedImages[1])
    print("result:", dieRollResult.result)
    #lm.showResult(dieRollResult.result)

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
        mm.setTopLed(int(sys.argv[2]))
        time.sleep(0.3)
        mm.setTopLed(0)
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
    print("not supported anymore. use mode 19 or motorTest.py")

elif mode == 17: # take pictures forever
    i = 0
    cam = Camera()
    dr = DieRecognizer()
    while True:
        print("take picture...")
        image = cam.takePicture()
        cam.close()
        print("analyze picture...")
        dieRollResult, processedImages = dr.getDieRollResult(image, returnOriginalImg=True)
        if i == 10:
            i = 0
            dr.writeImage(processedImages[1])
        i += 1
        print("waiting...")
        time.sleep(10)

elif mode == 18: # read and search dice dots #like mode 9 but read image and test timing on device...
    filename = 'test001'
    if len(sys.argv) > 2:
        filename = sys.argv[2]
    print("filename: ", filename)

    from tor.base.DieRecognizer import DieRecognizer
    dr = DieRecognizer()
    image = np.load(filename.format(".npy"))
    print("analyze picture...")
    t0 = time.time()
    dieRollResult, processedImages = dr.getDieRollResult(image, returnOriginalImg=True)
    print('timing of image analysis:', time.time()-t0)
    print("write image...")
    dr.writeImage(processedImages[1], filename.format("_result.jpg"))
    print("result:", dieRollResult.result)
    #lm.showResult(result)

# sudo torenv/bin/python3 -m tor.client.scripts.run 19 6 125 200 50 10 240 200 240 240 200 125 200 50 60 60 30 200 60 30 400
elif mode == 19: # move forever between two positions
    mm.doHoming()
    numOfPositions = int(sys.argv[2])
    index = 3
    positions = []
    for i in range(numOfPositions):
        pos = Position(float(sys.argv[index]), float(sys.argv[index+1]), float(sys.argv[index+2]))
        positions.append(pos)
        index += 3
    mm.setFeedratePercentage(float(sys.argv[index]))
    movementCount = 0
    while True:
        for pos in positions:
            mm.moveToPos(pos, segmented=True)
            mm.waitForMovementFinished(0.5)
        movementCount += 1
        if movementCount % 5 == 0:
            mm.doHoming()
        if movementCount % 20 == 0:
            print("movementCount: {}".format(movementCount))

elif mode == 20: #move through whole box and take images
    useTopLED = int(sys.argv[2])
    mm.doHoming()
    #xmin, xmax, dx = 5, 245, 30
    #ymin, ymax, dy = 120, 240, 30
    #zmin, zmax, dz = 60, 190, 30
    xmin, xmax, dx = 115, 135, 10
    ymin, ymax, dy = 210, 240, 10
    zmin, zmax, dz = 150, 190, 10
    lm = LedManager()
    cam = Camera()
    dr = DieRecognizer()
    lm.setAllLeds()
    if useTopLED:
        mm.setTopLed(cs.LED_TOP_BRIGHTNESS)
    for x in range(xmin, xmax+1, dx):
        for y in range(ymin, ymax+1, dy):
            for z in range(zmin, zmax+1, dz):
                pos = Position(x, y, z)
                mm.moveToPos(pos, segmented=True)
                mm.waitForMovementFinished(1)
                image = cam.takePicture()
                image = dr.transformImage(image)
                dr.writeImage(image, "image_{}.jpg".format(datetime.now().strftime("%Y%m%d%H%M%S")), directory=cs.IMAGE_DIRECTORY, doCreateDirectory=True)
    if useTopLED:
        mm.setTopLed(cs.LED_TOP_BRIGHTNESS_OFF)
    lm.clear()

elif mode == 21: #move to <n> random positions and take images
    useTopLED = int(sys.argv[2])
    nPositions = int(sys.argv[3])
    mm.doHoming()
    xmin, xmax = 5, 245
    ymin, ymax = 120, 240
    zmin, zmax = 50, 200
    #xmin, xmax = 115, 135
    #ymin, ymax = 205, 230
    #zmin, zmax = 170, 195
    lm = LedManager()
    cam = Camera()
    dr = DieRecognizer()
    lm.setAllLeds()
    if useTopLED:
        mm.setTopLed(cs.LED_TOP_BRIGHTNESS)
    for i in range(nPositions):
        x = random.randint(xmin, xmax)
        y = random.randint(ymin, ymax)
        z = random.randint(zmin, zmax)
        pos = Position(x, y, z)
        mm.moveToPos(pos, segmented=True)
        mm.waitForMovementFinished(1)
        image = cam.takePicture()
        image = dr.transformImage(image)
        dr.writeImage(image, "image_{}.jpg".format(datetime.now().strftime("%Y%m%d%H%M%S")), directory=cs.IMAGE_DIRECTORY, doCreateDirectory=True)
        print("{}/{}".format(i+1, nPositions))
    if useTopLED:
        mm.setTopLed(cs.LED_TOP_BRIGHTNESS_OFF)
    lm.clear()

elif mode == 22: #move to <n> random positions near cs.VERIFY_MAGNET_POSITION and take images
    useTopLED = int(sys.argv[2])
    nPositions = int(sys.argv[3])
    mm.doHoming()
    dx = 10
    dy = 10
    dz = 10
    lm = LedManager()
    cam = Camera()
    dr = DieRecognizer()
    lm.setAllLeds()
    if useTopLED:
        mm.setTopLed(cs.LED_TOP_BRIGHTNESS)
    for i in range(nPositions):
        pos = cs.VERIFY_MAGNET_POSITION + Position(random.randint(-dx, dx), random.randint(-dy, dy), random.randint(-dz, dz))
        mm.moveToPos(pos, segmented=True)
        mm.waitForMovementFinished(1)
        image = cam.takePicture()
        image = dr.transformImage(image)
        dr.writeImage(image, "image_{}.jpg".format(datetime.now().strftime("%Y%m%d%H%M%S")), directory=cs.IMAGE_DIRECTORY, doCreateDirectory=True)
        print("{}/{}".format(i+1, nPositions))
    if useTopLED:
        mm.setTopLed(cs.LED_TOP_BRIGHTNESS_OFF)
    lm.clear()

elif mode == 23:
    moveToCorrectPos = True if int(sys.argv[2]) == 1 else False
    mm.doHoming()
    if moveToCorrectPos:
        mm.moveToPos(cs.VERIFY_MAGNET_POSITION, True)
    else:
        mm.moveToPos(Position(220, 220, 150))
    mm.waitForMovementFinished(0.5)
    mr.verifyMagnetPosition()

elif mode == 24:
    import tor.TORSettings as ts
    from tor.base import NetworkUtils
    import socket
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((ts.SERVER_IP, ts.SERVER_PORT))

    im = [x for x in range(1234)]
    NetworkUtils.sendData(conn, im)
    answer = NetworkUtils.recvData(conn)
    conn.close()
    print("done")

# sudo torenv/bin/python3 -m tor.client.scripts.run 25 Y0 Y250
elif mode == 25: # move between two G-Code positions on a single motor
    from tor.client.Communicator import Communicator
    com = Communicator()
    coords = [sys.argv[2], sys.argv[3]]
    while True:
        for c in coords:
            com.send(f"G1 {c}")
            com.send("M400")
            com.recvUntilOk()
            com.send("M118 A1 move finished")
            com.recvUntilOk()

if mm is not None:
    mm.waitForMovementFinished(2)
    #mm.moveHome()


