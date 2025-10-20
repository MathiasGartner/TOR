import tor.client.ClientSettings as cs
from tor.base.LogManager import setupLogging, getLogger
setupLogging(cs.CLIENT_LOG_CONFIG_FILEPATH)
log = getLogger()

import argparse
from datetime import datetime, timedelta
import math
import time
import threading

import tor.TORSettings as ts
from tor.base.DieRecognizer import DieRecognizer
from tor.base.utils import Utils
from tor.base.utils.Point2D import Point2D
from tor.client.ClientManager import ClientManager
if cs.ON_RASPI:
    from tor.client.LedManager import LedManager
from tor.client.MovementManager import MovementManager
from tor.client.MovementRoutines import MovementRoutines
from tor.client.Position import Position

#################
### arguments ###
#################

parser = argparse.ArgumentParser()
parser.add_argument("-nohome", dest='skipHomingOnStartup', action="store_true")
args = parser.parse_args()

class ClientState:
    def __init__(self):
        # counter
        self.RunsSinceLastHoming = 0
        self.NoMagnetContact = 0
        self.NoMagnetContactGlobal = 0
        self.SameResultRecognized = 0
        self.NoResultRecognized = 0
        # last pos and result
        self.LastPickupPos = Point2D(0.5, 0.75)
        self.LastResult = -1
        self.UserModeTemporarilyDisabled = False

    def resetAllCounters(self):
        self.RunsSinceLastHoming = 0
        self.NoMagnetContact = 0
        self.NoMagnetContactGlobal = 0
        self.SameResultRecognized = 0
        self.NoResultRecognized = 0

def keepAskingForNextJob(askEveryNthSecond = None):
    global exitTOR
    global nextJob
    global userModeRequested
    global inUserMode
    global exitUserModeAtTime

    if askEveryNthSecond is None:
        askEveryNthSecond = cs.ASK_EVERY_NTH_SECOND_FOR_JOB

    standardWaitTime = askEveryNthSecond
    userModeWaitTime = cs.ASK_EVERY_NTH_SECOND_FOR_JOB_USERMODE

    while not exitTOR:
        if inUserMode:
            askEveryNthSecond = userModeWaitTime
        else:
            askEveryNthSecond = standardWaitTime
        nextTime = time.time() + askEveryNthSecond
        nextJob_ = cm.askForJob(inUserMode)
        lock.acquire()
        nextJob = nextJob_
        if "U" in nextJob:
            userModeRequested = True
        lock.release()
        if not inUserMode or ("A" in nextJob and nextJob["A"] != "NONE"):
            log.debug("nextJob: {}".format(nextJob))
        sleepFor = nextTime - time.time()
        if sleepFor > 0:
            time.sleep(sleepFor)

def updateClientIsActiveState():
    wasActive = cm.clientIsActive()
    cm.updateClientIsActive()
    isActive = cm.clientIsActive()
    log.info(f"wasActive: {wasActive}, isActive: {isActive}, if: {not wasActive and isActive}")
    if not wasActive and isActive:
        log.info("reactivated client, now homing...")
        mm.resetBoard()
        checkFunctionality()
        mm.doHoming()
        doHomingCheck()

def checkFunctionality():
    global lastFunctionalityCheckAtTime

    if lastFunctionalityCheckAtTime is None or datetime.now() > (lastFunctionalityCheckAtTime + timedelta(seconds=cs.MIN_TIME_BETWEEN_FUNCTIONALITY_CHECKS_S)):
        if cm.clientIsActive():
            if mm.checkOTPW():
                log.warning("OTPW triggered, client will be stopped")
                cm.sendStopClient("OTPW Triggered")
                cm.sendOTPWTriggered()
                updateClientIsActiveState()
            lastFunctionalityCheckAtTime = datetime.now()

def doHomingCheck():
    checkFunctionality()
    if cm.clientIsActive():
        lm.setAllLeds()
        homingSuccessful = mr.checkSuccessfulHoming()
        if not homingSuccessful:
            cm.sendStopClient("homing not successful")
            cm.sendHomingNotSuccessful()
            updateClientIsActiveState()

def waitUntilJobStarts(job):
    # TODO: allow for early exit of this (may be needed if nextJob changes during sleep)
    if "T" in job and job["T"] is not None and job["T"] != "None":
        startTime = datetime.strptime(job["T"], '%Y-%m-%d %H:%M:%S')
        startTimestamp = datetime.timestamp(startTime)
        Utils.sleepUntilTimestamp(startTimestamp)

def run():
    global state
    global userModeRequested
    global currentState

    doContinue = True
    doHoming = False

    lm.setAllLeds()

    # check early exit
    if not cm.clientIsActive() or userModeRequested:
        doContinue = False

    # roll
    currentState = "ROLL"
    magnetHadContact = False
    while doContinue and not magnetHadContact:
        if state.NoMagnetContact > 0:
            log.info(f"try roll count: {state.NoMagnetContact + 1}")
        log.info(f"last pickup pos {state.LastPickupPos}")
        dropoffPos = mr.run(state.LastPickupPos.x, numFailedTries=state.NoMagnetContact)
        magnetHadContact = mr.getLastMagnetContactStatus()
        if not magnetHadContact:
            if not state.UserModeTemporarilyDisabled:
                state.UserModeTemporarilyDisabled = True
                cm.setUserModeEnabled(False)
            state.NoMagnetContact += 1
            state.NoMagnetContactGlobal += 1
            cm.sendNoMagnetContact(dropoffPos, state.NoMagnetContactGlobal)
        if state.NoMagnetContactGlobal >= cs.MAX_COUNT_NO_MAGNET_CONTACT_GLOBAL:
            # pause
            log.warning("Reached maximum value for no magnet contact.")
            cm.sendStopClient("Maximum fails for magnet contact reached")
            cm.sendNoMagnetContactGlobal()
            updateClientIsActiveState()
            state.resetAllCounters()
            doContinue = False
        elif state.NoMagnetContact >= cs.MAX_COUNT_NO_MAGNET_CONTACT_RETRIES:
            state.NoMagnetContact = 0
            doHoming = True
            doContinue = False

        if doContinue:
            checkFunctionality()
        if not cm.clientIsActive() or userModeRequested:
            doContinue = False

    if doContinue:
        state.RunsSinceLastHoming += 1
        state.NoMagnetContact = 0
        state.NoMagnetContactGlobal = 0
        if state.RunsSinceLastHoming >= cs.HOME_EVERY_N_RUNS:
            cm.sendHomeAfterNSuccessfulRuns(state.RunsSinceLastHoming)
            state.RunsSinceLastHoming = 0
            doHoming = True
            doContinue = False

    if doContinue:
        # take image
        currentState = "PICKUP_TAKEIMAGE"
        dieRollResult = mr.pickupDie_takeImage()
        if userModeRequested:
            doContinue = False

    if doContinue:
        # pickup
        currentState = "PICKUP_PICKUP"
        if dieRollResult.found:
            state.NoResultRecognized = 0
        else:
            if not state.UserModeTemporarilyDisabled:
                state.UserModeTemporarilyDisabled = True
                cm.setUserModeEnabled(False)
            state.NoResultRecognized += 1
            log.info("No result recognized. Start search routine.")
            cm.sendDieResultNotFoundNTimes(state.NoResultRecognized)
            if state.NoResultRecognized < cs.HOME_AFTER_N_NOT_FOUND:
                currentState = "PICKUP_PICKUP"
                cm.sendSearchForDie()
                mr.searchForDie()
            elif state.NoResultRecognized == cs.HOME_AFTER_N_NOT_FOUND:
                doHoming = True
            elif state.NoResultRecognized > cs.HOME_AFTER_N_NOT_FOUND:
                # pause
                log.warning("Reached maximum value for no die recognized.")
                cm.sendStopClient("Maximum fails for die not recognized reached")
                cm.sendDieResultNotFoundMaxTimes()
                updateClientIsActiveState()
                state.resetAllCounters()
            doContinue = False

    if doContinue:
        # check if position is near old position
        distance = state.LastPickupPos.distance(dieRollResult.position)
        isNearOldPickupPosition = distance < cs.SAME_RESULT_NEAR_THRESHOLD
        if state.LastResult == dieRollResult.result and isNearOldPickupPosition:
            if not state.UserModeTemporarilyDisabled:
                state.UserModeTemporarilyDisabled = True
                cm.setUserModeEnabled(False)
            state.SameResultRecognized += 1
            log.warning(f"Same position and result recognized again ({state.SameResultRecognized + 1}). Distance from last result is only {distance:.5f}")
            cm.sendSameDieResultNTimes(state.SameResultRecognized + 1, dieRollResult.result, dieRollResult.position.x, dieRollResult.position.y)
            if state.SameResultRecognized <= cs.PAUSE_AFTER_N_SAME_RESULTS:
                # modified pickup
                if state.SameResultRecognized > 2:
                    log.warning("Pickup sideways")
                    mr.pickupDie_sideways(dieRollResult, leftright=(state.SameResultRecognized % 2) == 0, frontback=(state.SameResultRecognized % 2) == 1)
                else:
                    zOffset = cs.LOW_PICKUP_Z_OFFSET + state.SameResultRecognized
                    if dieRollResult.position.y < cs.NEAR_RAMP_Y and (state.SameResultRecognized % 2) == 0:
                        zOffset = -cs.HIGH_PICKUP_Z_OFFSET
                    log.warning(f"Pickup with extra z offset = {zOffset}")
                    mr.pickupDie_pickup(dieRollResult, zOffset=zOffset)
                checkFunctionality()
                if cm.clientIsActive():
                    # check if picked up
                    mm.moveToPos(cs.CENTER_TOP, True)
                    newDieRollResult = mr.pickupDie_takeImage()
                    if newDieRollResult.found:
                        distance = state.LastPickupPos.distance(newDieRollResult.position)
                        isNearOldPickupPosition = distance < cs.SAME_RESULT_NEAR_THRESHOLD
                        if state.LastResult == newDieRollResult.result and isNearOldPickupPosition:
                            # still on same position
                            log.info("still on same position, do homing")
                            doHoming = True
                            doContinue = False
                        else:
                            # on new position -> continue with normal pickup
                            dieRollResult = newDieRollResult
                    else:
                        # picked up
                        doContinue = False
                else:
                    doContinue = False
            else:
                # pause
                log.warning("Reached maximum value for same result recognized. Pausing.")
                cm.sendStopClient("Maximum value for same result recognized reached")
                cm.sendSameResultMaxTimes()
                updateClientIsActiveState()
                state.resetAllCounters()
                doContinue = False
        else:
            state.SameResultRecognized = 0

    if doContinue:
        currentState = "PICKUP_PICKUP"
        mr.pickupDie_pickup(dieRollResult, cm.sendDieRollResult)
        state.LastPickupPos = dieRollResult.position
        state.LastResult = dieRollResult.result
        checkFunctionality()

    if doHoming and cm.clientIsActive():
        homingResult = mr.pickupDieWhileHoming()
        if homingResult.found:
            state.NoResultRecognized = 0
        doHomingCheck()
        checkFunctionality()

    if state.UserModeTemporarilyDisabled and state.NoMagnetContact == 0 and state.NoMagnetContactGlobal == 0 and state.NoResultRecognized == 0 and state.SameResultRecognized == 0:
        state.UserModeTemporarilyDisabled = False
        cm.setUserModeEnabled(True)

    # this is always the last step if client is still active
    if cm.clientIsActive():
        mm.waitForMovementFinished()

def exitUserMode():
    global userModeRequested
    global inUserMode
    global currentState

    userModeRequested = False
    inUserMode = False
    currentState = ""

    cm.exitUserMode()
    lm.unloadUserMode()
    mm.setFeedratePercentage(cs.FR_DEFAULT)
    mm.moveToPos(cs.CENTER_TOP, True)
    mm.waitForMovementFinished()
    time.sleep(cs.STANDARD_CLIENT_SLEEP_TIME)
    lm.setAllLeds()

def doJobsDummy():
    global exitTOR
    global nextJob
    global inUserMode

    done = False
    while not done:
        log.debug("nextJob: {}".format(nextJob))
        if "T" in nextJob:
            test = datetime.strptime(nextJob["T"], '%Y-%m-%d %H:%M:%S')
            print(test)
        time.sleep(3)
    log.info("finished")
    exitTOR = True

def doJobs():
    global exitTOR
    global nextJob
    global inUserMode
    global userModeRequested
    global currentState
    global exitUserModeAtTime

    if not cm.clientIsActive():
        log.warning("client is not active")
    else:
        log.warning("current position: {}".format(MovementManager.currentPosition))

        checkFunctionality()

        if cm.clientIsActive():
            if not args.skipHomingOnStartup:
                mr.pickupDieWhileHoming()
            else:
                #TODO: get current position from BTT SKR Board
                #mm.refreshCurrentPositionFromBoard()
                #mm.setCurrentPositionGCode(cs.HOME_POSITION.toCordLengths())
                #MovementManager.currentPosition = cs.HOME_POSITION
                pass

            doHomingCheck()

    time.sleep(0.5)
    lm.setAllLeds()

    finishedRWRuns = 0
    finishedRWWaits = 0
    isFirstRWJob = True
    imagesTaken = 0
    inParkingPosition = False
    steppersDisabled = False
    done = False
    while not done:
        if not inUserMode:
            log.debug("doJobs loop")
            checkFunctionality()
            log.debug(f"client is active: {cm.clientIsActive()}")
        if "Q" in nextJob: # Q...quit
            done = True
            continue
        if not cm.clientIsActive():
            mm.disableSteppers()
            time.sleep(cs.UPDATE_ISACTIVE_SLEEP_TIME)
            updateClientIsActiveState()
            continue
        #log.info("nextJob: {}".format(nextJob))
        if not "W" in nextJob:
            inParkingPosition = False
            if not inUserMode:
                # this is no user mode state but used for a quick fix for clearing the wait status
                # needed in the Dashboard when turning off the whole installation
                cm.setUserModeReady("")
        if not "RW" in nextJob:
            finishedRWRuns = 0
            finishedRWWaits = 0
            isFirstRWJob = True
        if not "TAKE_IMAGE" in nextJob:
            imagesTaken = 0
        if not "W" in nextJob and not "RW" in nextJob:
            if steppersDisabled:
                mm.enableSteppers()
                mm.moveToParkingPosition(True)
                mm.waitForMovementFinished()
                steppersDisabled = False

        # do nextJob
        if "R" in nextJob:
            waitUntilJobStarts(nextJob)
            run()
        elif "RW" in nextJob:
            waitUntilJobStarts(nextJob)
            if nextJob["RW"] is None:
                runNTimes = 1
                waitNTimes = 1
                waitNSeconds = 1
            else:
                runWaitParams = nextJob["RW"].split()
                runNTimes = int(runWaitParams[0]) or 1
                waitNTimes = int(runWaitParams[1]) or 1
                waitNSeconds = int(runWaitParams[2]) or 1
            if isFirstRWJob:
                #waitNTimes = pow(math.sin(cm.clientIdentity.x + cm.clientIdentity.y + cm.clientIdentity.z)+ 1, 4) * 20
                cipos = 0 if cm.clientIdentity["Position"] is None else int(cm.clientIdentity["Position"])
                waitNTimes = pow(math.sin(cipos) + 1.2, 4) / 25.0 * (waitNTimes * waitNSeconds / 3)
            if finishedRWRuns < runNTimes:
                log.info("perform run {}/{} ...".format(finishedRWRuns+1, runNTimes))
                if steppersDisabled:
                    mm.enableSteppers()
                    mm.moveToParkingPosition(True)
                    mm.waitForMovementFinished()
                    steppersDisabled = False
                run()
                finishedRWRuns += 1
            elif finishedRWWaits < waitNTimes:
                currentState = "WAIT"
                if finishedRWWaits == 0:
                    mm.moveToDeepParkingPosition(True)
                    mm.waitForMovementFinished(cs.WAIT_BEFORE_DISABLE_STEPPER_TIME)
                    mm.disableSteppers()
                    steppersDisabled = True
                    log.info("wait time is {} seconds".format(waitNSeconds))
                log.info("perform wait {}/{} ...".format(finishedRWWaits+1, waitNTimes))
                time.sleep(waitNSeconds)
                finishedRWWaits += 1
            else:
                mm.enableSteppers()
                mm.moveToParkingPosition(True)
                mm.waitForMovementFinished()
                steppersDisabled = False
                finishedRWRuns = 0
                finishedRWWaits = 0
                isFirstRWJob = False
        elif "H" in nextJob: # H...homing
            mm.doHoming()
            doHomingCheck()
            mm.moveToPosAfterHoming(cs.CENTER_TOP, True)
            mm.waitForMovementFinished()
        elif "HH" in nextJob:  # H...homing with die pickup
            mr.pickupDieWhileHoming()
            mm.waitForMovementFinished()
            doHomingCheck()
            mm.moveToPosAfterHoming(cs.CENTER_TOP, True)
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
            elif performanceNo == 4:
                mr.doLightTest(startTime)
            elif performanceNo == 5:
                mr.doRollDie(startTime)
        elif "W" in nextJob: # W...wait
            waitUntilJobStarts(nextJob)
            currentState = "WAIT"
            if not inParkingPosition:
                mm.moveToParkingPosition(True)
                mm.waitForMovementFinished()
                mm.moveToDeepParkingPosition(True)
                mm.waitForMovementFinished(cs.WAIT_BEFORE_DISABLE_STEPPER_TIME)
                mm.disableSteppers()
                inParkingPosition = True
                steppersDisabled = True
                # this is no user mode state but used for a quick fix for setting the wait status
                # needed in the Dashboard when turning of the whole installation
                cm.setUserModeReady("WAITING")
            sleepTime = int(nextJob["W"] or cs.STANDARD_CLIENT_SLEEP_TIME)
            if sleepTime <= 0:
                sleepTime = cs.STANDARD_CLIENT_SLEEP_TIME
            time.sleep(sleepTime)
        elif "S" in nextJob: # S...load settings
            cm.loadSettings()
            cm.loadMeshpoints()
        elif "U" in nextJob: # U...user mode
            userModeRequested = False
            if not inUserMode:
                lm.clear()
                if currentState == "WAIT":
                    currentState = "ROLL"
                    pQuickRoll = threading.Thread(target=mr.doQuickRoll)
                    pLoadUserMode = threading.Thread(target=lm.loadUserMode)
                    pQuickRoll.start()
                    pLoadUserMode.start()
                    pQuickRoll.join()
                    pLoadUserMode.join()
                else:
                    lm.loadUserMode()
                inUserMode = True
                log.info("userModeReady: {}".format(currentState))
                cm.sendUserModeReady()
                if currentState == "":
                    currentState = "PICKUP_PICKUP"
                cm.setUserModeReady(currentState)
                mm.setFeedratePercentage(cs.FR_DEFAULT)
            exitUserModeAtTime = datetime.now() + timedelta(seconds=cs.EXIT_USER_MODE_AFTER_N_SECONDS + 10)
        elif "A" in nextJob: # A...action from user
            action = nextJob["A"]
            #log.info("action: {}".format(action))
            if action == "EXIT" or (exitUserModeAtTime is not None and datetime.now() > exitUserModeAtTime):
                exitUserMode()
            else:
                param = nextJob["PARAM"]
                mr.performUserAction(action, param)
                if action != "NONE":
                    exitUserModeAtTime = datetime.now() + timedelta(seconds=cs.EXIT_USER_MODE_AFTER_N_SECONDS)
        elif "TAKE_IMAGE" in nextJob: # take test images
            imageType = nextJob["TAKE_IMAGE"]
            if imagesTaken > cs.HOME_AFTER_N_IMAGES_TAKEN:
                mr.pickupDieWhileHoming()
                mm.waitForMovementFinished()
                mm.moveToPosAfterHoming(cs.CENTER_TOP, True)
                mm.waitForMovementFinished()
                imagesTaken = 0
            if imageType == "MAGNET_POS_TRUE" or imageType == "MAGNET_POS_FALSE" or imageType == "MAGNET_POS_TEST":
                go = True
                prefix = ""
                distance = 6
                wrongDistance = distance * 1.5
                dx = 10 * time.time() % (2 * distance) - distance
                dy = 10 * dx % (2 * distance) - distance
                dz = 10 * dy % (2 * distance) - distance
                if imageType == "MAGNET_POS_TRUE":
                    pos = cs.VERIFY_MAGNET_POSITION + Position(dx, dy, dz)
                    prefix = "ok"
                elif imageType == "MAGNET_POS_FALSE":
                    prefix = "wrong"
                    posDiff = Position(10*dx, 4*(dy-7), 3*(dz-8))
                    if abs(posDiff.x) <= wrongDistance and abs(posDiff.y) <= wrongDistance and abs(posDiff.z) <= wrongDistance:
                        go = False
                    else:
                        pos = cs.VERIFY_MAGNET_POSITION + posDiff
                elif imageType == "MAGNET_POS_TEST":
                    prefix = "test"
                    pos = cs.VERIFY_MAGNET_POSITION + Position(5 * dx, 2 * (dy-5), 3 * dz)
                if go:
                    im = mr.moveToPosAndTakeMagnetVerificationImage(pos)
                    dr.writeImage(im, "{}_id={}_{}.png".format(prefix, cm.clientId, Utils.getFilenameTimestamp()), cs.IMAGE_DIRECTORY_POSITION, doCreateDirectory=True)
                    imagesTaken += 1


    if cm.clientIsActive():
        if steppersDisabled:
            mm.enableSteppers()
            steppersDisabled = False
        mm.moveToParkingPosition(True)

    log.info("finished")
    exitTOR = True

####################
###    tests     ###
####################


###################
###    main     ###
###################

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

dr = DieRecognizer()
mm = MovementManager()
if not mm.hasCorrectVersion:
    log.warning("Incompatible version of TOR-Marlin installed. TORClient will now quit.")
    exit(0)
mr = MovementRoutines(cm, mm)

if cs.ON_RASPI:
    try:
        lm = LedManager()
    except:
        raise Exception("Could not create LedManager.")

####################
### main program ###
####################

lock = threading.Lock()
exitTOR = False
nextJob = ""
userModeRequested = False
currentState = ""
inUserMode = False
exitUserModeAtTime = None
lastFunctionalityCheckAtTime = None

jobScheduler = threading.Thread(target=keepAskingForNextJob)
jobScheduler.start()

state = ClientState()

if cs.ON_RASPI:
    worker = threading.Thread(target=doJobs)
else:
    worker = threading.Thread(target=doJobsDummy)
worker.start()

worker.join()
exitTOR = True # worker quitted accidentally

time.sleep(5)
if cm.clientIsActive():
    mm.waitForMovementFinished()
    mm.moveToParkingPosition(True)

jobScheduler.join()
#lm.clear()
log.info("TORClient will now quit.")
