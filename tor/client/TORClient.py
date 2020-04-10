from random import randint
from random import seed
import socket
import sys
import time

from tor.base import NetworkUtils
from tor.base.DiceRecognizer import DiceRecognizer
import tor.client.ClientSettings as cs
if cs.ON_RASPI:
    from tor.client.Camera import Camera
from tor.client.MovementManager import MovementManager
import tor.TORSettings as ts

def createConnection():
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((ts.SERVER_IP, ts.SERVER_PORT))
    return conn

def askForJob():
    conn = createConnection()
    NetworkUtils.sendData(conn, {"C" : clientId, "J" : "waiting"})
    answer = NetworkUtils.recvData(conn)
    conn.close()
    return answer

def sendDieRollResult(result):
    conn = createConnection()
    dieRoll = {
        "C" : clientId,
        "D" : result
    }
    NetworkUtils.sendData(conn, dieRoll)
    answer = NetworkUtils.recvData(conn)
    if "STATUS" in answer:
        print("server responds", answer["STATUS"])
    conn.close()

def sendDieNotFound():
    #TODO: send message to server that die could not be located
    pass

def sendDieResultNotRecognized():
    #TODO: send message to server that die could not be located
    pass

def doDieRoll():
    mm.rollDie()
    time.sleep(cs.DIE_ROLL_TIME)
    if cs.ON_RASPI:
        image = cam.takePicture()
    else:
        image = dr.readDummyImage()
    (found,x,y,result) = dr.getDiePosition(image)
    if found:
        if not result > 0:
            result = dr.getDieResult()
        if not result > 0:
            result = dr.getDieResultWithExtensiveProcessing()
        if result > 0:
            sendDieRollResult(result)
        else:
            sendDieResultNotRecognized()
        mm.moveToXYPosDiceAndRamp(x, y)
        mm.waitForMovementFinished()
        if not dr.checkIfDiePickedUp():
            mm.searchForDie()
            mm.waitForMovementFinished()
            mm.moveToYPosRamp(cs.LY/2)
            mm.waitForMovementFinished()
    else:
        sendDieNotFound()
        mm.searchForDie()
        mm.moveToYPosRamp(cs.LY/2)
        mm.waitForMovementFinished()

seed(12345)

clientId = 1
if len(sys.argv) > 1:
    clientId = int(sys.argv[1])

if cs.ON_RASPI:
    cam = Camera()

dr = DiceRecognizer()

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

