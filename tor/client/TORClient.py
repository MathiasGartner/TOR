import datetime
import numpy as np
from random import randint
from random import seed
import sys
import time
import threading

from tor.base import NetworkUtils
from tor.base.DieRecognizer import DieRecognizer
from tor.client.ClientManager import ClientManager
import tor.client.ClientSettings as cs

if cs.ON_RASPI:
    from tor.client.Camera import Camera
    from tor.client.LedManager import LedManager
from tor.client.MovementManager import MovementManager

def keepAskingForNextJob(askEveryNthSecond = 10):
    global nextJob
    while True:
        nextTime = time.time() + askEveryNthSecond
        nextJob = cm.askForJob()
        print("nextJob", nextJob)
        sleepFor = nextTime - time.time()
        #print("sleep for", sleepFor)
        if sleepFor > 0:
            time.sleep(sleepFor)

def doDieRoll():
    print("doDieRoll()")
    mm.moveToPos(cs.DROPOFF_ADVANCE_POSITION)
    mm.waitForMovementFinished()
    mm.setFeedratePercentage(cs.DROPOFF_ADVANCE_FEEDRATE)
    mm.moveToPos(cs.DROPOFF_POSITION, segmented=True)
    mm.setFeedratePercentage(cs.FEEDRATE_PERCENTAGE)

    #dropoff_cords = cs.DROPOFF_POSITION.toCordLengths()
    #print(dropoff_cords)
    #dropoff_cords.lengths[0] += 1
    #dropoff_cords.lengths[3] += 1
    #print(dropoff_cords)
    #mm.moveToCords(dropoff_cords)

    mm.waitForMovementFinished()
    time.sleep(2)
    mm.rollDie()
    time.sleep(cs.DIE_ROLL_TIME / 2)
    mm.moveToPos(cs.CENTER_TOP)
    mm.waitForMovementFinished()
    time.sleep(cs.DIE_ROLL_TIME / 2)
    print("take picture...")
    if cs.ON_RASPI:
        image = cam.takePicture()
    else:
        image = dr.readDummyImage()
    print("analyze picture...")
    found, diePosition, result, processedImages = dr.getDiePosition(image, returnOriginalImg=True)
    print("write image...")
    dr.writeImage(processedImages[1])
    print("send result...")
    if found:
        print("found @", diePosition)
        if not result > 0:
            result = dr.getDieResult()
        if not result > 0:
            result = dr.getDieResultWithExtensiveProcessing()
        if result > 0:
            print("die result:", result)
            #lm.showResult(result)
            cm.sendDieRollResult(result)
        else:
            cm.sendDieResultNotRecognized()
        mm.moveToXYPosDie(diePosition.x, diePosition.y)
        mm.moveToPos(cs.CENTER_TOP)
        if not dr.checkIfDiePickedUp():
            mm.searchForDie()
            mm.waitForMovementFinished()
    else:
        cm.sendDieNotFound()
        mm.searchForDie()
    #mm.moveToXPosRamp(cs.LX/2)
    mm.moveToPos(cs.DROPOFF_ADVANCE_POSITION)
    mm.waitForMovementFinished()

def doJobsDummy():
    global nextJob
    done = False
    while not done:
        print(nextJob)
        time.sleep(3)
    print("finished")

def doJobs():
    global nextJob
    mm.initBoard()
    mm.doHoming()
    mm.moveToPos(cs.CENTER_TOP)
    mm.waitForMovementFinished()
    print("now in starting position.")
    time.sleep(0.5)

    done = False
    while not done:
        print(nextJob)
        if "R" in nextJob:
            for _ in range(int(nextJob["R"])):
                doDieRoll()
        elif "C" in nextJob:
            mm.moveToAllCorners()
            mm.waitForMovementFinished()
        elif "M" in nextJob:
            if "P" in nextJob:
                pos = None
                if nextJob["P"] == "BOTTOM_CENTER":
                    pos = cs.CENTER_BOTTOM
                elif nextJob["P"] == "CX":
                    pos = [cs.CENTER_TOP, cs.CORNER_X, cs.CENTER_TOP]
                elif nextJob["P"] == "CY":
                    pos = [cs.CENTER_TOP, cs.CORNER_Y, cs.CENTER_TOP]
                elif nextJob["P"] == "CZ":
                    pos = [cs.CENTER_TOP, cs.CORNER_Z, cs.CENTER_TOP]
                elif nextJob["P"] == "CE":
                    pos = [cs.CENTER_TOP, cs.CORNER_E, cs.CENTER_TOP]
                if pos is not None:
                    mm.moveToPos(pos)
                    mm.waitForMovementFinished()
                    time.sleep(1)
            elif "H" in nextJob:
                mm.doHoming()
                mm.moveToPos(cs.CENTER_TOP)
                mm.waitForMovementFinished()
        elif "W" in nextJob:
            if "T" in nextJob:
                waitUntil = nextJob["T"]
                while datetime.datetime.now() < waitUntil:
                    time.sleep(1)
            if "S" in nextJob:
                time.sleep(nextJob["S"])
        elif "Q" in nextJob:
            done = True
    mm.moveHome()
    print("finished")

####################
###    tests     ###
####################


####################
### main program ###
####################

seed(12345)

#get client identity
cm = ClientManager()
welcomeMessage = "I am client \"{}\" with ID {} and IP {}. My ramp is made out of {}, mounted on position {}"
print("#######################")
print(welcomeMessage.format(cm.clientIdentity["Name"], cm.clientId, cm.clientIdentity["IP"], cm.clientIdentity["Material"], cm.clientIdentity["Position"]))
print("#######################")

#load custom settings from file and server
ccsModuleName = "tor.client.CustomClientSettings." + cm.clientIdentity["Material"]
try:
    import importlib
    customClientSettings = importlib.import_module(ccsModuleName)
except:
    print("No CustomClientSettings found.")

meshBed, meshRamp, meshMagnet = cm.getMeshpoints()

if cs.ON_RASPI:
    try:
        cam = Camera()
    except:
        raise Exception("Could not connect to camera.")
    try:
        lm = LedManager()
    except:
        raise Exception("Could not connect to LED strip.")

dr = DieRecognizer()

mm = MovementManager()

nextJob = ""

jobScheduler = threading.Thread(target=keepAskingForNextJob)
jobScheduler.start()

if cs.ON_RASPI:
    worker = threading.Thread(target=doJobs)
else:
    worker = threading.Thread(target=doJobsDummy)
worker.start()

