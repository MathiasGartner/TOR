import argparse
from datetime import datetime
import logging
import numpy as np
import time
import threading

import tor.TORSettings as ts
from tor.base.DieRecognizer import DieRecognizer
from tor.base.DieRollResult import DieRollResult
from tor.client.ClientManager import ClientManager
import tor.client.ClientSettings as cs

if cs.ON_RASPI:
    from tor.client.LedManager import LedManager
from tor.client.MovementManager import MovementManager
from tor.client.MovementRoutines import MovementRoutines

#################
### arguments ###
#################

parser = argparse.ArgumentParser()
parser.add_argument("-nohome", dest='doHomingOnStartup', action="store_false")
args = parser.parse_args()

def keepAskingForNextJob(askEveryNthSecond = 10):
    global exitTOR
    global nextJob
    while not exitTOR:
        nextTime = time.time() + askEveryNthSecond
        nextJob = cm.askForJob()
        log.info("nextJob: {}".format(nextJob))
        sleepFor = nextTime - time.time()
        if sleepFor > 0:
            time.sleep(sleepFor)

def run():
    global runsSinceLastHoming
    global lastPickupX
    global countNotFound
    global countSameResult
    global lastResult

    lm.setAllLeds()

    dieRollResult = mr.run(lastPickupX, cm.sendDieRollResult)
    if dieRollResult.found:
        lastPickupX = dieRollResult.position.x
        #cm.sendDieRollResult(dieRollResult)
        if lastResult == dieRollResult.result:
            countSameResult += 1
        else:
            countSameResult = 0
        lastResult = dieRollResult.result
        countNotFound = 0
    else:
        lastPickupX = cs.LX / 2.0
        cm.sendDieResultNotRecognized()
        countNotFound += 1

    #check if homing is needed
    runsSinceLastHoming += 1
    if runsSinceLastHoming >= cs.HOME_EVERY_N_RUNS:
        mm.doHoming()
        mm.moveToPos(cs.CENTER_TOP)
        runsSinceLastHoming = 0
    elif countNotFound >= cs.HOME_AFTER_N_FAILS:
        log.info("count not found: {} -> do homing...".format(countNotFound))
        mm.doHoming()
        mm.moveToPos(cs.BEFORE_PICKUP_POSITION)
        mr.searchForDie()
        mm.moveToPos(cs.CENTER_TOP, True)
        countNotFound = 0
        runsSinceLastHoming = 0
    elif countSameResult >= cs.HOME_AFTER_N_SAME_RESULTS:
        log.info("count same result: {} -> do homing...".format(countSameResult))
        dieRollResult, processedImages = mr.findDieWhileHoming()
        mm.waitForMovementFinished()
        mm.moveToPos(cs.BEFORE_PICKUP_POSITION)
        if dieRollResult.found:
            mr.pickupDieFromPosition(dieRollResult.position)
        else:
            mr.searchForDie()
        mm.moveToPos(cs.CENTER_TOP, True)
        countSameResult = 0
        runsSinceLastHoming = 0

    mm.waitForMovementFinished()

def doJobsDummy():
    global exitTOR
    global nextJob
    done = False
    while not done:
        log.info("nextJob: {}".format(nextJob))
        if "T" in nextJob:
            test = datetime.strptime(nextJob["T"], '%Y-%m-%d %H:%M:%S')
            print(test)
        time.sleep(3)
    log.info("finished")
    exitTOR = True

def doJobs():
    global exitTOR
    global nextJob

    log.warning("current position: {}".format(MovementManager.currentPosition))

    if args.doHomingOnStartup:
        dieRollResult, processedImages = mr.findDieWhileHoming()
        mm.waitForMovementFinished()

        mm.setFeedratePercentage(cs.FR_SLOW_MOVE)
        mm.moveToPos(cs.CENTER_TOP)
        if dieRollResult.found:
            mr.pickupDieFromPosition(dieRollResult.position)
    else:
        #TODO: get current position from BTT SKR Board
        mm.setCurrentPositionGCode(cs.HOME_POSITION.toCordLengths())
        MovementManager.currentPosition = cs.HOME_POSITION

    mm.setFeedratePercentage(cs.FR_SLOW_MOVE)
    mm.moveToPos(cs.CENTER_TOP, True)
    mm.waitForMovementFinished()
    log.info("now in starting position.")
    time.sleep(0.5)

    lm.setAllLeds()

    done = False
    while not done:
        log.info("nextJob: {}".format(nextJob))
        if "R" in nextJob:
            run()
        elif "H" in nextJob: # H...homing
            mm.doHoming()
            mm.moveToPos(cs.CENTER_TOP)
            mm.waitForMovementFinished()
        elif "HH" in nextJob:  # H...homing
            mr.findDieWhileHoming()
            mm.waitForMovementFinished()
            mm.moveToPos(cs.CENTER_TOP)
            mm.waitForMovementFinished()
        elif "P" in nextJob: # P...Performance
            if "T" in nextJob:
                startTime = datetime.strptime(nextJob["T"], '%Y-%m-%d %H:%M:%S')
            else:
                startTime = datetime.now()
            performanceNo = int(nextJob["P"]) or 1
            if performanceNo == 1:
                mr.doTestPerformance(startTime)
            elif performanceNo == 2:
                mr.doDieRollAndPickupPerformance(startTime)
            elif performanceNo == 3:
                mr.doPositionTestWithTiming(startTime, cm.clientIdentity, cm.x, cm.y, cm.z)
        elif "W" in nextJob: # W...wait
            sleepTime = int(nextJob["W"] or cs.STANDARD_CLIENT_SLEEP_TIME)
            if sleepTime <= 0:
                sleepTime = cs.STANDARD_CLIENT_SLEEP_TIME
            time.sleep(sleepTime)
        elif "Q" in nextJob: # Q...quit
            done = True
        elif "S" in nextJob: # S...load settings
            cm.loadSettings()
    mm.moveToParkingPosition(True)
    log.info("finished")
    exitTOR = True

####################
###    tests     ###
####################


###################
###    main     ###
###################

logging.basicConfig(format='%(levelname)s: %(message)s', level=cs.LOG_LEVEL)
log = logging.getLogger(__name__)

###########################
### get client identity ###
###########################

serverAvailable = False
serverWaitTime = 1
serverWaitTimeIncrease = 1

while not serverAvailable:
    try:
        cm = ClientManager()
        serverAvailable = True
    except:
        log.warning("Could not connect to TORServer@{}:{}".format(ts.SERVER_IP, ts.SERVER_PORT))
        time.sleep(serverWaitTime)
        serverWaitTime += serverWaitTimeIncrease

welcomeMessage = "I am client with ID {} and IP {}. My ramp is made out of {}, mounted on position {}"
log.info("#######################")
log.info(welcomeMessage.format(cm.clientId, cm.clientIdentity["IP"], cm.clientIdentity["Material"], cm.clientIdentity["Position"]))
log.info("#######################")

### load custom settings from file and server
ccsModuleName = "tor.client.CustomClientSettings." + cm.clientIdentity["Material"]
try:
    import importlib
    customClientSettings = importlib.import_module(ccsModuleName)
    print("Custom config file loaded.")
except:
    log.warning("No CustomClientSettings found.")

cm.loadSettings()
cm.loadMeshpoints()

log.setLevel(cs.LOG_LEVEL)

dr = DieRecognizer()
mm = MovementManager()
if not mm.hasCorrectVersion:
    log.warning("Incompatible version of TOR-Marlin installed. TORClient will now quit.")
    exit(0)
mr = MovementRoutines()

if cs.ON_RASPI:
    try:
        lm = LedManager()
    except:
        raise Exception("Could not create LedManager.")

####################
### main program ###
####################

exitTOR = False
nextJob = ""

jobScheduler = threading.Thread(target=keepAskingForNextJob)
jobScheduler.start()

runsSinceLastHoming = 0
lastPickupX = cs.LX / 2.0
countNotFound = 0
countSameResult = 0
lastResult = -1
if cs.ON_RASPI:
    worker = threading.Thread(target=doJobs)
else:
    worker = threading.Thread(target=doJobsDummy)
worker.start()

worker.join()
exitTOR = True # worker quitted accidentally
mm.moveToParkingPosition(True)
jobScheduler.join()
lm.clear()
log.info("TORClient will now quit.")
