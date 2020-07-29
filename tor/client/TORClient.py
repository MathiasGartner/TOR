import datetime
import numpy as np
import time
import threading

from tor.base.DieRecognizer import DieRecognizer
from tor.client.ClientManager import ClientManager
import tor.client.ClientSettings as cs

if cs.ON_RASPI:
    from tor.client.LedManager import LedManager
from tor.client.MovementManager import MovementManager
from tor.client.MovementRoutines import MovementRoutines
from tor.client.Position import Position

def keepAskingForNextJob(askEveryNthSecond = 10):
    global exitTOR
    global nextJob
    while not exitTOR:
        nextTime = time.time() + askEveryNthSecond
        nextJob = cm.askForJob()
        print("nextJob", nextJob)
        sleepFor = nextTime - time.time()
        #print("sleep for", sleepFor)
        if sleepFor > 0:
            time.sleep(sleepFor)

def run():
    global runsSinceLastHoming
    global lastPickupX
    global countNotFound
    global countSameResult
    global lastResult

    # move to dropoff position
    #TODO: remove random, interpolate dropoffPos for lastPickupX
    mm.setFeedratePercentage(cs.FR_DEFAULT)
    dropoffPos = cs.MESH_MAGNET[np.random.randint(0, len(cs.MESH_MAGNET)), :]
    mm.moveToPos(Position(dropoffPos[0], dropoffPos[1] + 20, 30), True)
    mm.setFeedratePercentage(cs.FR_DROPOFF_ADVANCE)
    mm.moveToPos(Position(dropoffPos[0], dropoffPos[1] + 10, dropoffPos[2] + 10), True)
    mm.setFeedratePercentage(cs.FR_DROPOFF_ADVANCE_SLOW)
    mm.moveToPos(Position(dropoffPos[0], dropoffPos[1], dropoffPos[2]), True)
    mm.waitForMovementFinished()

    # roll die
    time.sleep(cs.WAIT_BEFORE_ROLL_TIME)
    mm.setFeedratePercentage(cs.FR_FAST_MOVES)
    mm.rollDie()
    time.sleep(cs.DIE_ROLL_TIME / 2.0)
    mm.moveToPos(cs.CENTER_TOP)
    time.sleep(cs.DIE_ROLL_TIME / 2.0)

    # pickup die
    found, result, diePosition = mr.pickupDie()
    if found:
        lastPickupX = diePosition.x
        cm.sendDieRollResult(result)
        if lastResult == result:
            countSameResult += 1
        else:
            countSameResult = 0
        lastResult = result
    else:
        lastPickupX = cs.LX / 2.0
        cm.sendDieResultNotRecognized()
        countNotFound += 1

    #check if homing is needed
    runsSinceLastHoming += 1
    if runsSinceLastHoming >= cs.HOME_EVERY_N_RUNS:
        mm.doHoming()
        runsSinceLastHoming = 0
    elif countNotFound >= cs.HOME_AFTER_N_FAILS:
        mm.doHoming()
        mr.searchForDie()
        countNotFound = 0
    elif countSameResult >= cs.HOME_AFTER_N_SAME_RESULTS:
        mm.doHoming()
        #TODO: while homing, check if image recognition finds die
        #      for this, add option "waitForHomingFinished" to mm.doHoming()
        #      then eihter call mr.searchForDie() or mr.pickupDie() or nothing?
        mr.searchForDie()
        countSameResult = 0

    mm.moveToPos(cs.CENTER_TOP)
    mm.waitForMovementFinished()

def doJobsDummy():
    global exitTOR
    global nextJob
    done = False
    while not done:
        print(nextJob)
        time.sleep(3)
    print("finished")
    exitTOR = True

def doJobs():
    global exitTOR
    global nextJob
    mm.doHoming()
    mm.moveToPos(cs.CENTER_TOP)
    mm.waitForMovementFinished()
    print("now in starting position.")
    time.sleep(0.5)

    done = False
    while not done:
        print(nextJob)
        if "R" in nextJob:
            run()
        elif "H" in nextJob: # H...homing
            mm.doHoming()
            mm.moveToPos(cs.CENTER_TOP)
            mm.waitForMovementFinished()
        elif "W" in nextJob: # W...wait
            time.sleep(nextJob["W"])
        elif "Q" in nextJob: # Q...quit
            done = True
    mm.moveToParkingPosition()
    print("finished")
    exitTOR = True

####################
###    tests     ###
####################


###########################
### get client identity ###
###########################

cm = ClientManager()
welcomeMessage = "I am client with ID {} and IP {}. My ramp is made out of {}, mounted on position {}"
print("#######################")
print(welcomeMessage.format(cm.clientId, cm.clientIdentity["IP"], cm.clientIdentity["Material"], cm.clientIdentity["Position"]))
print("#######################")

### load custom settings from file and server
ccsModuleName = "tor.client.CustomClientSettings." + cm.clientIdentity["Material"]
try:
    import importlib
    customClientSettings = importlib.import_module(ccsModuleName)
except:
    print("No CustomClientSettings found.")

cm.loadSettings()
cm.loadMeshpoints()

dr = DieRecognizer()
mm = MovementManager()
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

jobScheduler.join()
worker.join()
print("TORClient will now quit.")
