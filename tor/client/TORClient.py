from random import randint
from random import seed
import socket
import sys
import time

from tor.base import NetworkUtils
from tor.base.DieRecognizer import DieRecognizer
import tor.client.ClientSettings as cs
if cs.ON_RASPI:
    from tor.client.Camera import Camera
from tor.client.MovementManager import MovementManager
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
        "E" : 1,
        "MESSAGE" : "Could not recognize die result."
    }
    answer = sendAndGetAnswer(msg)

def doDieRoll():
    mm.rollDie()
    time.sleep(cs.DIE_ROLL_TIME)
    if cs.ON_RASPI:
        image = cam.takePicture()
    else:
        image = dr.readDummyImage()
    found, diePosition, result, processedImages = dr.getDiePosition(image, returnOriginalImg=True)
    dr.writeImage(processedImages[1])
    if found:
        if not result > 0:
            result = dr.getDieResult()
        if not result > 0:
            result = dr.getDieResultWithExtensiveProcessing()
        if result > 0:
            sendDieRollResult(result)
        else:
            sendDieResultNotRecognized()
        mm.moveToXYPosDieAndRamp(diePosition.x, diePosition.y)
        mm.waitForMovementFinished()
        if not dr.checkIfDiePickedUp():
            mm.searchForDie()
            mm.waitForMovementFinished()
            mm.moveToXPosRamp(cs.LX/2)
            mm.waitForMovementFinished()
    else:
        sendDieNotFound()
        #mm.searchForDie()
        #mm.moveToXPosRamp(cs.LX/2)
        mm.waitForMovementFinished()

seed(12345)

clientId = 1
if len(sys.argv) > 1:
    clientId = int(sys.argv[1])

if cs.ON_RASPI:
    cam = Camera()

dr = DieRecognizer()

mm = MovementManager()

mm.initBoard()
mm.setCurrentPosition(cs.HOME_CORDS)
mm.getCurrentPosition()
time.sleep(0.5)

for _ in range(1):
    doDieRoll()

answer = askForJob()
print(answer)
if "R" in answer:
    for _ in range(answer["R"]):
        doDieRoll()

mm.moveHome()
print("finished")

