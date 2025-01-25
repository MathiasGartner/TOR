import logging
log = logging.getLogger(__name__)

import socket
import subprocess

from tor.base import NetworkUtils

import tor.client.ClientSettings as cs
import tor.TORSettings as ts

def getServiceStatusTORClient():
    isActive = False
    val = subprocess.call(["systemctl", "is-active", "--quiet", "TORClient"])
    if val == 0:
        isActive = True
    return isActive

def startServiceTORClient():
    cmd = ["sudo", "systemctl", "daemon-reload"]
    subprocess.call(cmd)
    cmd = ["sudo", "systemctl", "restart", "TORClient"]
    subprocess.call(cmd)

def stopServiceTORClient():
    cmd = ["sudo", "systemctl", "stop", "TORClient"]
    subprocess.call(cmd)

def handleRequest(conn):
    request = NetworkUtils.recvData(conn)
    if isinstance(request, dict):
        log.info(request)
        if "TYPE" in request:
            if request["TYPE"] == "STATUS":
                serviceTORClientRunning = getServiceStatusTORClient()
                msg = {
                        "TOR_VERSION": ts.VERSION_TOR,
                        "TOR_CLIENT_SERVICE": "active" if serviceTORClientRunning else "inactive"
                      }
                NetworkUtils.sendData(conn, msg)
                log.info(msg)
            else:
                log.warning(f"request type not defined: {request['TYPE']}")
        elif "LED" in request:
            from tor.client.LedManager import LedManager
            lm = LedManager()
            if request["LED"] == "ON":
                lm.setAllLeds()
            else:
                lm.clear()
            NetworkUtils.sendOK(conn)
        elif "TORCLIENT" in request:
            if request["TORCLIENT"] == "START":
                startServiceTORClient()
            else:
                stopServiceTORClient()
            NetworkUtils.sendOK(conn)
        else:
            log.warning("request not defined: {}".format(request))
    else:
        log.warning("request not defined: {}".format(request))

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=cs.LOG_LEVEL_STATUS)
log = logging.getLogger(__name__)

ownIP = NetworkUtils.getOwnIP()
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((ownIP, ts.STATUS_PORT))
serverSocket.listen(10)

log.info("start status manager")
while True:
    (clientSocket, address) = serverSocket.accept()
    handleRequest(clientSocket)