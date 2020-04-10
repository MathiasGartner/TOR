import json
import socket

from tor.base import NetworkUtils
import tor.TORSettings as ts

msgOK = json.dumps({"STATUS" : "OK"})

def handleRequest(conn):
    request = NetworkUtils.recvData(conn)
    if "C" in request:
        clientId = request["C"]
        if "D" in request:
            diceResult = request["D"]
            print("Client", clientId, "rolled", diceResult)
            conn.send(msgOK.encode())
        elif "E" in request:
            print("ERROR", request["E"])
        elif "J" in request:
            print("client asks for job")
            NetworkUtils.sendData(conn, {"R" : 2})
    else:
        print("could not identify client.")

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((ts.SERVER_IP, ts.SERVER_PORT))
serverSocket.listen(5)

print("start server")
while True:
    (clientSocket, address) = serverSocket.accept()
    handleRequest(clientSocket)
