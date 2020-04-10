from random import randint
from random import seed
import socket
import sys
import time

from tor.base import NetworkUtils
import tor.client.ClientSettings as cs
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

def doDieRoll():
    mm.moveToXYPosDiceAndRamp(100, 130)
    mm.waitForMovementFinished(0)
    time.sleep(1)
    dieResult = randint(1, 6)
    sendDieRollResult(dieResult)
    time.sleep(1)
    mm.moveHome()
    mm.waitForMovementFinished(0)

seed(12345)

clientId = 1
if len(sys.argv) > 1:
    clientId = int(sys.argv[1])

mm = MovementManager()

mm.initBoard()
mm.setCurrentPosition(cs.HOME_CORDS)
mm.getCurrentPosition()
time.sleep(0.5)

for _ in range(3):
    doDieRoll()

answer = askForJob()
print(answer)
if "R" in answer:
    for _ in range(answer["R"]):
        doDieRoll()

print("finished")

