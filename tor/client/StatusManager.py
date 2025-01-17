import logging
log = logging.getLogger(__name__)

import socket

from tor.base import NetworkUtils

import tor.client.ClientSettings as cs
import tor.TORSettings as ts

def handleRequest(conn):
    request = NetworkUtils.recvData(conn)
    if isinstance(request, dict):
        log.info(request)
        if "TYPE" in request:
            if request["TYPE"] == "STATUS":
                msg = {
                        "TOR_VERSION": ts.VERSION_TOR,
                        "TOR_CLIENT_SERVICE": "unknown"
                      }
                NetworkUtils.sendData(conn, msg)
                log.info(msg)
            else:
                log.warning(f"request type not defined: {request['TYPE']}")
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