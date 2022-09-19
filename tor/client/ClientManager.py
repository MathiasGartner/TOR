import logging
log = logging.getLogger(__name__)

import numpy as np
import socket

from tor.base import NetworkUtils
import tor.client.ClientSettings as cs
import tor.TORSettings as ts

class ClientManager:
    def __init__(self):
        self.clientMacAddress = NetworkUtils.getMAC()
        if cs.ON_RASPI:
            self.clientIdentity = self.askForClientIdentity(self.clientMacAddress)
        else:
            self.clientIdentity = { "Id": -1, "IP": -1, "Material": "vacuum", "Position": -1, "Latin": "vacuum", "IsActive": 0 }
        self.clientId = self.clientIdentity["Id"]
        p = int(self.clientIdentity["Position"])
        if (p - 1) % 9 < 3:
            self.x = 0
        elif (p - 1) % 9 < 6:
            self.x = 1
        else:
            self.x = 2
        if p < 10:
            self.y = 0
        elif p < 19:
            self.y = 1
        else:
            self.y = 2
        self.z = (p - 1) % 3

    def createConnection(self):
        conn = None
        ok = False
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((ts.SERVER_IP, ts.SERVER_PORT))
            ok = True
        except Exception as e:
            log.error("Error while connecting to TORServer:")
            log.error("{}".format(repr(e)))
        if not ok:
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

    def updateClientIsActive(self):
        updatedClientIdentity = self.askForClientIdentity(self.clientMacAddress)
        self.clientIdentity["IsActive"] = updatedClientIdentity["IsActive"]

    def sendDieRollResult(self, dieRollResult, userGenerated=False):
        msg = {
            "C": self.clientId,
            "RESULT": dieRollResult.result,
            "POSX": dieRollResult.position.x,
            "POSY": dieRollResult.position.y,
            "USER": userGenerated,
        }
        answer = self.sendAndGetAnswer(msg)
        if "STATUS" in answer:
            log.debug("server response: {}".format(answer["STATUS"]))

    def sendDieNotFound(self):
        msg = {
            "C": self.clientId,
            "E": "NOT_LOC",
            "MESSAGE": "Could not locate die."
        }
        answer = self.sendAndGetAnswer(msg)

    def sendDieResultNotRecognized(self):
        msg = {
            "C": self.clientId,
            "E": "NOT_REC",
            "MESSAGE": "Could not recognize die result."
        }
        answer = self.sendAndGetAnswer(msg)

    def sendDieResultNotFoundNTimes(self, n):
        msg = {
            "C": self.clientId,
            "E": "NOT_FOUND_N",
            "MESSAGE": "Could not find die {} times.".format(n)
        }
        answer = self.sendAndGetAnswer(msg)

    def sendSameDieResultNTimes(self, n, result):
        msg = {
            "C": self.clientId,
            "E": "SAME_RESULT_N",
            "MESSAGE": "Got the same results {} times in a row. Always find a {}".format(n, result)
        }
        answer = self.sendAndGetAnswer(msg)

    def sendStopClient(self, msg):
        msg = {
            "C": self.clientId,
            "STOP": msg
        }
        answer = self.sendAndGetAnswer(msg)

    def sendHomeAfterNSuccessfulRuns(self, n):
        msg = {
            "C": self.clientId,
            "MSG": "HOME_N_SUCCESS",
            "MESSAGE": "YEAH! I am now homing after {} successful runs in a row.".format(n)
        }
        answer = self.sendAndGetAnswer(msg)

    def sendUserModeReady(self):
        msg = {
            "C": self.clientId,
            "MSG": "USERMODE_READY",
            "MESSAGE": "Started user mode."
        }
        answer = self.sendAndGetAnswer(msg)

    def askForJob(self, inUserMode=False):
        if inUserMode:
            msg = {"C": self.clientId, "A": ""}
        else:
            msg = {"C": self.clientId, "J": ""}
        answer = self.sendAndGetAnswer(msg)
        return answer

    def askMagnetPositionIsOK(self, image):
        msg = {
            "C": self.clientId,
            "MAGNET_POSITION_IMAGE": image
        }
        answer = self.sendAndGetAnswer(msg)
        isOK = answer["POSITION_OK"]
        return isOK == 1

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
        log.info("{}".format(settings))
        availableSettingTypes = {
            "USE_MAGNET_BETWEEN_P0P1": "BOOL",
            "USE_MAGNET_BETWEEN_P2P3": "BOOL",
            "ALWAYS_USE_PX": "INT",
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
                    log.info("Set {}={}".format(name, value))
                    setattr(cs, name, value)
                else:
                    log.warning("Failed setting {}={}".format(name, raw_value))

    def saveDropoffPointSettings(self):
        msg = {
            "C": self.clientId,
            "PUT": "SETTINGS",
            "SETTINGS": [
                ["USE_MAGNET_BETWEEN_P0P1", cs.USE_MAGNET_BETWEEN_P0P1],
                ["USE_MAGNET_BETWEEN_P2P3", cs.USE_MAGNET_BETWEEN_P2P3],
                ["ALWAYS_USE_PX", cs.ALWAYS_USE_PX]
            ]
        }
        answer = self.sendAndGetAnswer(msg)
        # TODO: check server response

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

    def exitUserMode(self):
        msg = {
            "C": self.clientId,
            "U": "EXIT"
        }
        answer = self.sendAndGetAnswer(msg)

    def setUserModeReady(self, state):
        msg = {
            "C": self.clientId,
            "U": state
        }
        answer = self.sendAndGetAnswer(msg)
