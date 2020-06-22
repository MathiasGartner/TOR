import datetime
import json
import random
import socket

from tor.base import DBManager
from tor.base import NetworkUtils
import tor.TORSettings as ts

msgOK = json.dumps({"STATUS" : "OK"})

def log(*msg):
    print('{0:%Y-%m-%d %H:%M:%S}: '.format(datetime.datetime.now()), end='')
    print(msg)

def handleRequest(conn):
    request = NetworkUtils.recvData(conn)
    if "C" in request:
        clientId = request["C"]
        if "D" in request:
            dieResult = request["D"]
            log("Client", clientId, "rolled", dieResult)
            conn.send(msgOK.encode())
            DBManager.writeResult(clientId, dieResult)
        elif "E" in request:
            log("ERROR", request["E"], "@ client", clientId)
            log(request["MESSAGE"])
            conn.send(msgOK.encode())
        elif "J" in request:
            #jobIds = [1, 1, 1, 1, 1, 1, 3, 4, 5, 6, 7, 8]
            jobIds = [1]
            job = random.choice(jobIds)
            log("client", clientId, "asks for job, send", job)
            if job == 1:
                NetworkUtils.sendData(conn, {"R" : 1})
            elif job == 2:
                NetworkUtils.sendData(conn, {"C" : 1})
            elif job == 3: #move to center bottom
                NetworkUtils.sendData(conn, {"M": 1, "P" : "CENTER_BOTTOM"})
            elif job == 4: #move to CX
                NetworkUtils.sendData(conn, {"M": 1, "P" : "CX"})
            elif job == 5: #move to CY
                NetworkUtils.sendData(conn, {"M": 1, "P" : "CY"})
            elif job == 6: #move to CZ
                NetworkUtils.sendData(conn, {"M": 1, "P" : "CZ"})
            elif job == 7: #move to CE
                NetworkUtils.sendData(conn, {"M": 1, "P" : "CE"})
            elif job == 8: #do homing
                NetworkUtils.sendData(conn, {"H": 1})
    elif "ID" in request:
        cId = DBManager.getClientIdentity(request["ID"])
        NetworkUtils.sendData(conn, {"Id": cId.Id,
                                     "IP": cId.IP,
                                     "Name": cId.Name,
                                     "Material": cId.Material
                                     })
    else:
        log("could not identify client.")

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((ts.SERVER_IP, ts.SERVER_PORT))
serverSocket.listen(5)

log("start server")
while True:
    (clientSocket, address) = serverSocket.accept()
    handleRequest(clientSocket)
