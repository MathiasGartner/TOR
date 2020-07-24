import socket

from tor.base import NetworkUtils
import tor.client.ClientSettings as cs
import tor.TORSettings as ts

class ClientManager:
    def __init__(self):
        self.clientMacAddress = NetworkUtils.getMAC()
        self.clientIdentity = self.askForClientIdentity(self.clientMacAddress)
        self.clientId = self.clientIdentity["Id"]

    def createConnection(self):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((ts.SERVER_IP, ts.SERVER_PORT))
        return conn

    def sendAndGetAnswer(self, msg):
        conn = self.createConnection()
        NetworkUtils.sendData(conn, msg)
        answer = NetworkUtils.recvData(conn)
        conn.close()
        return answer

    def askForClientIdentity(self, macAddress):
        msg = {"MAC": macAddress}
        answer = self.sendAndGetAnswer(msg);
        return answer

    def sendDieRollResult(self, result):
        msg = {
            "C": self.clientId,
            "D": result
        }
        answer = self.sendAndGetAnswer(self, msg)
        if "STATUS" in answer:
            print("server responds", answer["STATUS"])

    def sendDieNotFound(self):
        msg = {
            "C": self.clientId,
            "E": 1,
            "MESSAGE": "Could not locate die."
        }
        answer = self.sendAndGetAnswer(msg)

    def sendDieResultNotRecognized(self):
        msg = {
            "C": self.clientId,
            "E": 2,
            "MESSAGE": "Could not recognize die result."
        }
        answer = self.sendAndGetAnswer(msg)

    def askForJob(self):
        msg = {"C": self.clientId, "J": "waiting"}
        answer = self.sendAndGetAnswer(msg)
        return answer

    def getMeshpoints(self):
        meshBed = cs.MESH_BED_DEFAULT
        meshRamp = cs.MESH_BED_DEFAULT
        meshMagnet = cs.MESH_BED_DEFAULT
        msg = {
            "C": self.clientId,
            "GET": "MESH"
        }
        answer = self.sendAndGetAnswer(msg)
        if "B" in answer:
            meshBed = answer["B"]
        if "R" in answer:
            meshRamp = answer["R"]
        if "M" in answer:
            meshMagnet = answer["M"]
        return meshBed, meshRamp, meshMagnet

    def saveMeshpoints(self, type, points):
        msg = {
            "C": self.clientId,
            "PUT": "MESH",
            "TYPE": type,
            "POINTS": points
        }
        answer = self.sendAndGetAnswer(msg)
        # TODO: check server response
