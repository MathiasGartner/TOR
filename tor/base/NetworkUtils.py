import logging
log = logging.getLogger(__name__)

import json
import numpy as np

import tor.client.ClientSettings as cs

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

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def recvData(conn):
    msgReceived = conn.recv(4096)
    msg = msgReceived.decode()
    msgData = json.loads(msg)
    return msgData

def sendData(conn, data):
    msgToSend = json.dumps(data, cls=NumpyEncoder)
    conn.send(msgToSend.encode())

def sendOK(conn):
    msgOK = json.dumps({"STATUS" : "OK"})
    conn.send(msgOK.encode())