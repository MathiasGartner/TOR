import json

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

def recvData(conn):
    msgReceived = conn.recv(4096)
    msg = msgReceived.decode()
    msgData = json.loads(msg)
    return msgData

def sendData(conn, data):
    msgToSend = json.dumps(data)
    conn.send(msgToSend.encode())