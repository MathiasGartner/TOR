import argparse
import cv2
import time
import numpy as np
import os

from tor.client import ClientSettings as cs
from tor.client.MovementManager import MovementManager
from tor.client.MovementRoutines import MovementRoutines
from tor.client.Position import Position
from tor.base.DieRecognizer import DieRecognizer
from tor.client.Camera import Camera
from tor.client.ClientManager import ClientManager
from tor.client.LedManager import LedManager


#################
### arguments ###
#################

parser = argparse.ArgumentParser()
parser.add_argument("position", nargs='*', default=[cs.CENTER_TOP.x, cs.CENTER_TOP.y, cs.CENTER_TOP.z], type=float)
parser.add_argument("-f", dest="feedratePercentage", default=cs.FR_DEFAULT, type=int)
parser.add_argument("-c", dest="doHoming", action="store_true")
parser.add_argument("-l", dest="led", action="store_true")
parser.add_argument("-p", dest="take_picture", action="store_true")
parser.add_argument("-s", dest="segmented", action="store_true")
parser.add_argument("-start", dest='start', action="store_true")
parser.add_argument("-find", dest='find', action="store_true")
parser.add_argument("-pickup", dest='pickup', action="store_true")
parser.add_argument("-infinity", dest='infinity', action="store_true")
parser.add_argument("-cor", dest="cal_on_run", default=0, type=int)
args = parser.parse_args()


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

mm = MovementManager()
mr = MovementRoutines()
lm = LedManager()

def start_script():
    spos = cs.MESH_MAGNET[np.random.randint(0, 4), :]
    mm.waitForMovementFinished()
    mm.moveToPos(Position(spos[0], spos[1]+20, 50), True)
    mm.waitForMovementFinished()
    mm.setFeedratePercentage(50)
    mm.moveToPos(Position(spos[0], spos[1]+10, spos[2]+10), True)
    mm.waitForMovementFinished()
    mm.setFeedratePercentage(30)
    mm.moveToPos(Position(spos[0], spos[1], spos[2]), True)
    mm.waitForMovementFinished()
    mm.setFeedratePercentage(450)
    time.sleep(1)
    mm.rollDie()
    if (args.find):
        time.sleep(2)
        found, result, diePosition = mr.pickupDie()
        return found, result


###############
### Program ###
###############

if args.feedratePercentage != cs.FR_DEFAULT:
    mm.setFeedratePercentage(args.feedratePercentage)

if args.doHoming:
    mm.doHoming()
    exit(0)

if args.pickup:
    mr.pickupDie()
    exit(0)

if args.start:
    if (args.infinity):
        i=0
        err=0
        result=-1
        while(True):
            i+=1
            if (err == 3):  # prevents bad runs
                err = 0
                i = 1
                mm.doHoming()
                mr.searchForDie()

            result_old = result
            found, result = start_script()
            print(result)

            if ((not found) or (result_old == result)):
                err += 1
            else:
                err = 0

            if(args.cal_on_run > 0):
                if(np.mod(i,args.cal_on_run)==0):
                    mm.doHoming()
                    mm.waitForMovementFinished()
    else:
        start_script()
    exit(0)

pos = Position(args.position[0], args.position[1], args.position[2])
if pos.isValid():
    mm.moveToPos(pos, args.segmented)

