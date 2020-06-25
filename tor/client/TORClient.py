from random import randint
from random import seed
import socket
import sys
import time

from tor.base import NetworkUtils
from tor.base.DieRecognizer import DieRecognizer
import tor.client.ClientSettings as cs
from tor.client.Cords import Cords

if cs.ON_RASPI:
    from tor.client.Camera import Camera
#from tor.client.LedManager import LedManager
from tor.client.MovementManager import MovementManager
from tor.client.Position import Position
import tor.TORSettings as ts

def createConnection():
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((ts.SERVER_IP, ts.SERVER_PORT))
    return conn

def sendAndGetAnswer(msg):
    conn = createConnection()
    NetworkUtils.sendData(conn, msg)
    answer = NetworkUtils.recvData(conn)
    conn.close()
    return answer

def askForClientIdentity(name):
    msg = {"ID" : name}
    answer = sendAndGetAnswer(msg);
    return answer

def askForJob():
    msg = {"C" : clientId, "J" : "waiting"}
    answer = sendAndGetAnswer(msg)
    return answer

def sendDieRollResult(result):
    msg = {
        "C" : clientId,
        "D" : result
    }
    answer = sendAndGetAnswer(msg)
    if "STATUS" in answer:
        print("server responds", answer["STATUS"])

def sendDieNotFound():
    msg = {
        "C" : clientId,
        "E" : 1,
        "MESSAGE" : "Could not locate die."
    }
    answer = sendAndGetAnswer(msg)

def sendDieResultNotRecognized():
    msg = {
        "C" : clientId,
        "E" : 2,
        "MESSAGE" : "Could not recognize die result."
    }
    answer = sendAndGetAnswer(msg)

def doDieRoll():
    print("doDieRoll()")
    mm.moveToPos(cs.DROPOFF_ADVANCE_POSITION)
    mm.waitForMovementFinished()

    mm.moveToPos(cs.DROPOFF_POSITION, segmented=True)

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
            sendDieRollResult(result)
        else:
            sendDieResultNotRecognized()
        mm.moveToXYPosDie(diePosition.x, diePosition.y)
        mm.moveToPos(cs.CENTER_TOP)
        if not dr.checkIfDiePickedUp():
            mm.searchForDie()
            mm.waitForMovementFinished()
    else:
        sendDieNotFound()
        mm.searchForDie()
    #mm.moveToXPosRamp(cs.LX/2)
    mm.moveToPos(cs.DROPOFF_ADVANCE_POSITION)
    mm.waitForMovementFinished()

seed(12345)

clientName = "C1"
if len(sys.argv) > 1:
    clientName = sys.argv[1]

if cs.ON_RASPI:
    cam = Camera()

dr = DieRecognizer()

mm = MovementManager()

#lm = LedManager()

cId = askForClientIdentity(clientName)
clientId = cId["Id"]
print("I am client \"{}\" with ID {} and my ramp is made out of {}".format(cId["Name"], cId["Id"], cId["Material"]))

mm.initBoard()
mm.doHoming()
mm.moveToPos(cs.CENTER_TOP)
mm.waitForMovementFinished()
print("now in starting position.")
time.sleep(0.5)

done = False
while not done:
    answer = askForJob()
    print(answer)
    if "R" in answer:
        for _ in range(answer["R"]):
            doDieRoll()
    elif "C" in answer:
        mm.moveToAllCorners()
        mm.waitForMovementFinished()
    elif "M" in answer:
        if "P" in answer:
            pos = None
            if answer["P"] == "BOTTOM_CENTER":
                pos = cs.CENTER_BOTTOM
            elif answer["P"] == "CX":
                pos = [cs.CENTER_TOP, cs.CORNER_X, cs.CENTER_TOP]
            elif answer["P"] == "CY":
                pos = [cs.CENTER_TOP, cs.CORNER_Y, cs.CENTER_TOP]
            elif answer["P"] == "CZ":
                pos = [cs.CENTER_TOP, cs.CORNER_Z, cs.CENTER_TOP]
            elif answer["P"] == "CE":
                pos = [cs.CENTER_TOP, cs.CORNER_E, cs.CENTER_TOP]
            if pos is not None:
                mm.moveToPos(pos)
                mm.waitForMovementFinished()
                time.sleep(1)
        elif "H" in answer:
            mm.doHoming()
            mm.moveToPos(cs.CENTER_TOP)
            mm.waitForMovementFinished()
    elif "Q" in answer:
        done = True

mm.moveHome()
print("finished")

