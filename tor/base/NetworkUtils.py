import json

def recvData(conn):
    msgReceived = conn.recv(4096)
    msg = msgReceived.decode()
    msgData = json.loads(msg)
    return msgData

def sendData(conn, data):
    msgToSend = json.dumps(data)
    conn.send(msgToSend.encode())