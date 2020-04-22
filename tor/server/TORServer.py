import json
import random
import socket

from tor.base import NetworkUtils
import tor.TORSettings as ts

msgOK = json.dumps({"STATUS" : "OK"})

def handleRequest(conn):
    request = NetworkUtils.recvData(conn)
    if "C" in request:
        clientId = request["C"]
        if "D" in request:
            dieResult = request["D"]
            print("Client", clientId, "rolled", dieResult)
            conn.send(msgOK.encode())
        elif "E" in request:
            print("ERROR", request["E"], "@ client", clientId)
            print(request["MESSAGE"])
            conn.send(msgOK.encode())
        elif "J" in request:
            jobIds = [1, 3, 4, 5, 6, 7]
            job = random.choice(jobIds)
            print("client", clientId, "asks for job, send", job)
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
    else:
        print("could not identify client.")

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((ts.SERVER_IP, ts.SERVER_PORT))
serverSocket.listen(5)

print("start server")
while True:
    (clientSocket, address) = serverSocket.accept()
    handleRequest(clientSocket)
