import numpy as np
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
        answer = self.sendAndGetAnswer(msg)
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

    def loadMeshpoints(self):
        cs.MESH_BED = cs.MESH_BED_DEFAULT
        cs.MESH_RAMP = cs.MESH_RAMP_DEFAULT
        cs.MESH_MAGNET = cs.MESH_MAGNET_DEFAULT
        msg = {
            "C": self.clientId,
            "GET": "MESH"
        }
        answer = self.sendAndGetAnswer(msg)
        if "B" in answer:
            cs.MESH_BED = np.array(answer["B"])
        if "R" in answer:
            cs.MESH_RAMP = np.array(answer["R"])
        if "M" in answer:
            cs.MESH_MAGNET = np.array(answer["M"])

    def saveMeshpoints(self, type, points):
        msg = {
            "C": self.clientId,
            "PUT": "MESH",
            "TYPE": type,
            "POINTS": points
        }
        answer = self.sendAndGetAnswer(msg)
        # TODO: check server response

    def loadSettings(self):
        msg = {
            "C": self.clientId,
            "GET": "SETTINGS"
        }
        settings = self.sendAndGetAnswer(msg)
        print(settings)
        availableSettingTypes = {
            "IMAGE_CROP_X_LEFT": "INT",
            "IMAGE_CROP_X_RIGHT": "INT",
            "IMAGE_CROP_Y_TOP": "INT",
            "IMAGE_CROP_Y_BOTTOM": "INT",
            "TRY_FINDING": "BOOL",
            "CAM_ISO": "INT",
            "CAM_SHUTTER_SPEED": "INT",
            "CAM_CONTRAST": "INT",
            "CAM_AWBR": "FLOAT",
            "CAM_AWBB": "FLOAT",
            "IMG_USE_WARPING": "BOOL",
            "IMG_TL": "LIST",
            "IMG_BL": "LIST",
            "IMG_TR": "LIST",
            "IMG_BR": "LIST",
        }
        for name, raw_value in settings:
            value = None
            if name in availableSettingTypes:
                datatype = availableSettingTypes[name]
                if datatype == "INT":
                    value = int(raw_value)
                elif datatype == "FLOAT":
                    value = float(raw_value)
                elif datatype == "STRING":
                    value = str(raw_value)
                elif datatype == "BOOL":
                    value = bool(int(raw_value))
                elif datatype == "LIST":
                    value = eval(raw_value)
                if value is not None:
                    print("Set", name, "=", value)
                    setattr(cs, name, value)
                else:
                    print("ERROR setting", name, "=", raw_value)

    def saveCameraSettings(self):
        msg = {
            "C": self.clientId,
            "PUT": "SETTINGS",
            "SETTINGS": [
                ["CAM_ISO", cs.CAM_ISO],
                ["CAM_SHUTTER_SPEED", cs.CAM_SHUTTER_SPEED],
                ["CAM_CONTRAST", cs.CAM_CONTRAST],
                ["CAM_AWBR", cs.CAM_AWBR],
                ["CAM_AWBB", cs.CAM_AWBB]
            ]
        }
        answer = self.sendAndGetAnswer(msg)
        # TODO: check server response

    def saveImageSettingsWarping(self, tl, bl, tr, br):
        msg = {
            "C": self.clientId,
            "PUT": "SETTINGS",
            "SETTINGS": [
                ["IMG_USE_WARPING", True],
                ["IMG_TL", tl],
                ["IMG_BL", bl],
                ["IMG_TR", tr],
                ["IMG_BR", br]
            ]
        }
        answer = self.sendAndGetAnswer(msg)
        # TODO: check server response

    def saveImageSettingsCropping(self, tl, br):
        msg = {
            "C": self.clientId,
            "PUT": "SETTINGS",
            "SETTINGS": [
                ["IMG_USE_WARPING", False],
                ["IMG_TL", tl],
                ["IMG_BR", br]
            ]
        }
        answer = self.sendAndGetAnswer(msg)
        # TODO: check server response