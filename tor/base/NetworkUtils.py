from tor.base.LogManager import getLogger
log = getLogger("NetworkUtils")

import json
import numpy as np
import socket

import tor.client.ClientSettings as cs
import tor.TORSettings as ts

def getMACLinux(interface='wlan0'):
    try:
        str = open('/sys/class/net/%s/address' % interface).read()
    except:
        str = "00:00:00:00:00:00"
    return str[0:17]

def getMACWindows():
    return "60:57:18:a7:99:e1" #YOGA
    from uuid import getnode
    try:
        mac = getnode()
        str = "".join(c + ":" if i % 2 else c for i, c in enumerate(hex(mac)[2:].zfill(12)))[:-1]
    except:
        str = "00:00:00:00:00:00"
    return str

def getMAC(interface='wlan0'):
  try:
    if cs.ON_RASPI:
        mac = getMACLinux(interface)
    else:
        mac = getMACWindows()
  except:
    mac = "00:00:00:00:00:00"
  return mac

def getOwnIP():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        log.error("Error getting own IP:")
        log.error("{}".format(repr(e)))
    return ip

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def createServerConnection():
    conn = createConnection(ts.SERVER_IP, ts.SERVER_PORT)
    if conn is None:
        log.error("Could not connect to TORServer")
    return conn

def createConnection(ip, port, timeout=None, verbose=True):
    conn = None
    ok = False
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if timeout is not None:
            conn.settimeout(timeout)
        conn.connect((ip, port))
        ok = True
    except Exception as e:
        if verbose:
            log.error(f"Error while connecting to {ip}:{port}")
            log.error("{}".format(repr(e)))
        conn = None
    #TODO: why is this done a second time??
    #if not ok:
    #    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #    if timeout is not None:
    #        conn.settimeout(timeout)
    #    conn.connect((ip, port))
    return conn

def recvData(conn):
    msgData = None
    if conn is not None:
        msgReceived = conn.recv(ts.MAX_MSG_LENGTH)
        fullMessage = msgReceived
        while (len(msgReceived) == ts.MAX_MSG_LENGTH):
            msgReceived = conn.recv(ts.MAX_MSG_LENGTH)
            fullMessage += msgReceived
        #print("finished receiving")
        #print("len recv TOTAL:", len(fullMessage))
        msg = fullMessage.decode()
        if len(msg) > 0:
            try:
                msgData = json.loads(msg)
            except Exception as e:
                log.error("Error parsing JSON message:")
                log.error("{}".format(repr(e)))
                log.error("msg: {}".format(msg))
                import traceback
                log.error(traceback.format_exc())
    return msgData

def sendData(conn, data):
    msgToSend = json.dumps(data, cls=NumpyEncoder)
    if conn is not None:
        sent = conn.send(msgToSend.encode())
        #print("sent: {}".format(sent))
    else:
        log.error(f"cannot send {msgToSend}")

def sendOK(conn):
    msgOK = json.dumps({"STATUS" : "OK"})
    conn.send(msgOK.encode())

def sendNotOK(conn):
    msgNotOK = json.dumps({"STATUS" : "NOT OK"})
    conn.send(msgNotOK.encode())
