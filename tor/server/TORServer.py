import tor.server.ServerSettings as ss
from tor.base.LogManager import setupLogging, getLogger
setupLogging(ss.SERVER_LOG_CONFIG_FILEPATH)
log = getLogger()

import copy
import numpy as np
import socket

from tor.base import DBManager
from tor.base import MailManager
from tor.base import NetworkUtils
from tor.base.utils import Utils
from tor.base.PositionVerification import PositionVerification
from tor.server.Job import DefaultJobs
import tor.TORSettings as ts

def getClientSettings(clientId):
    settings = DBManager.getClientSettings(clientId)
    return settings

def saveClientSettings(clientId, settings):
    DBManager.saveClientSettings(clientId, settings)

def getMeshpoints(clientId):
    meshpoints = DBManager.getMeshpoints(clientId)
    meshTypes = ["B", "R", "M"]
    groupedPoints = {}
    for t in meshTypes:
        points = [(float(x), float(y), float(z)) for (ty, no, x, y, z) in meshpoints if ty == t]
        if len(points) > 0:
            groupedPoints[t] = points
    return groupedPoints

def saveMeshpoints(clientId, type, points):
    DBManager.saveMeshpoints(clientId, type, points)

def exitUserMode(clientId):
    DBManager.exitUserMode(clientId)

def setCurrentStateForUserMode(clientId, state):
    DBManager.setCurrentStateForUserMode(clientId, state)

def handleRequest(conn):
    request = NetworkUtils.recvData(conn)
    if isinstance(request, dict):
        if "C" in request: #request from client C
            clientId = request["C"]
            if "RESULT" in request: #die roll result
                dieResult = request["RESULT"]
                x = request["POSX"]
                y = request["POSY"]
                userGenerated = request["USER"]
                log.info("Client {} rolled {} at [{}, {}]".format(clientId, dieResult, x, y))
                NetworkUtils.sendOK(conn)
                DBManager.writeResult(clientId, dieResult, x, y, userGenerated, ts.DICE_RESULT_EVENT_SOURCE)
            elif "E" in request: #error on client
                log.warning("Error {} @ Client {}".format(request["E"], clientId))
                log.warning(request["MESSAGE"])
                DBManager.logClientAction(clientId, "ERROR", request["E"], request["MESSAGE"])
                NetworkUtils.sendOK(conn)
            elif "WARN" in request: #warning on client
                log.warning("Warning {} @ Client {}".format(request["WARN"], clientId))
                log.warning(request["MESSAGE"])
                DBManager.logClientAction(clientId, "WARNING", request["WARN"], request["MESSAGE"])
                NetworkUtils.sendOK(conn)
            elif "MSG" in request: # message for logging
                log.info("Message {} @ Client {}".format(request["MSG"], clientId))
                log.warning(request["MESSAGE"])
                DBManager.logClientAction(clientId, "INFO", request["MSG"], request["MESSAGE"])
                NetworkUtils.sendOK(conn)
            elif "J" in request: #client asks for job
                job = DBManager.getNextJobForClientIdOnSchedule(clientId)
                log.debug("client {} asks for job, send {}".format(clientId, job))
                NetworkUtils.sendData(conn, {
                    job.JobCode: job.JobParameters,
                    "T": job.ExecuteAt.__str__()
                })
            elif "U" in request:
                if request["U"] == "EXIT":
                    exitUserMode(clientId)
                else:
                    setCurrentStateForUserMode(clientId, request["U"])
                NetworkUtils.sendOK(conn)
            elif "USER_MODE" in request:
                DBManager.setUserModeEnabled(clientId, request["USER_MODE"])
                NetworkUtils.sendOK(conn)
            elif "A" in request:
                log.info("send next user action")
                action = DBManager.getUserAction(clientId)
                #log.info("action: {}".format(action))
                NetworkUtils.sendData(conn, {
                    "A": action["Action"],
                    "PARAM": action["Parameters"]
                })
            elif "GET" in request:
                if request["GET"] == "MESH":
                    meshpoints = getMeshpoints(clientId)
                    NetworkUtils.sendData(conn, meshpoints)
                elif request["GET"] == "SETTINGS":
                    settings = getClientSettings(clientId)
                    NetworkUtils.sendData(conn, settings)
            elif "PUT" in request:
                if request["PUT"] == "MESH":
                    NetworkUtils.sendOK(conn)
                    saveMeshpoints(clientId, request["TYPE"], request["POINTS"])
                elif request["PUT"] == "SETTINGS":
                    NetworkUtils.sendOK(conn)
                    saveClientSettings(clientId, request["SETTINGS"])
            elif "MAGNET_POSITION_IMAGE" in request:
                # TOOD: make this thread safe
                im = request["MAGNET_POSITION_IMAGE"]
                isOK = False
                if clientId in pvs and pvs[clientId].isInitialized:
                    isOK = pvs[clientId].verifyPosition(im)
                elif pv.isInitialized:
                    isOK = pv.verifyPosition(im)
                else:
                    isOK = True
                #if datetime.datetime.now().minute > 13:
                #    isOK = False
                NetworkUtils.sendData(conn, {
                    "POSITION_OK": 1 if isOK else 0,
                })
                prefix = "ok" if isOK else "wrong"
                Utils.writeImage(np.array(im).astype(np.float32), "production_{}_id={}_{}.png".format(prefix, clientId, Utils.getFilenameTimestamp()), ss.TOR_MAGNET_PICTURE_DIRECTORY, doCreateDirectory=True)
            elif "STOP" in request:
                DBManager.setClientIsActive(clientId, False)
                jW = copy.deepcopy(DefaultJobs.WAIT)
                jW.ClientId = clientId
                DBManager.saveJobs(jW)
                cId = DBManager.getClientIdentityByClientId(clientId)
                errorLog = DBManager.getClientLogByClientId(clientId, 20)
                MailManager.sendDeactiveClient(cId, request["STOP"], errorLog)
                NetworkUtils.sendOK(conn)
        elif "MAC" in request:
            cId = DBManager.getClientIdentity(request["MAC"])
            if cId is not None:
                NetworkUtils.sendData(conn, {"Id": cId.Id,
                                             "IP": cId.IP,
                                             "Material": cId.Material,
                                             "Position": cId.Position,
                                             "Latin": cId.Latin,
                                             "IsActive": cId.IsActive
                                             })
            else:
                log.warning(f"Could not load Client Identity for {request['MAC']}.")
                NetworkUtils.sendNotOK(conn)
        elif "DASH" in request: #status request from Dashboard UI
            NetworkUtils.sendOK(conn)
        else:
            log.warning("could not identify sender.")
    else:
        log.warning("request not defined: {}".format(request))


pv = PositionVerification()
pvs = {}

if ss.VERIFY_MAGNET_BY_CLIENTID:
    ids = ts.CLIENT_IDS
    for id in ids:
        pvs[id] = PositionVerification(clientId=id)

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((ts.SERVER_IP, ts.SERVER_PORT))
serverSocket.listen(10)

log.info("start server")
while True:
    (clientSocket, address) = serverSocket.accept()
    handleRequest(clientSocket)

