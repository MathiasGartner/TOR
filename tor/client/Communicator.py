import serial
import sys

import tor.client.ClientSettings as cs

class Communicator:
    def __init__(self, serialPort = ""):
        if serialPort == "":
            if cs.ON_RASPI:
                #serialPort = "/dev/ttyACM0"
                serialPort = "/dev/ttyS0"
        if serialPort == "":
            self.useSerial = False
        else:
            self.useSerial = True
            self.ser = serial.Serial(
                port=serialPort,
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )

    def send(self, message):
        if self.useSerial:
            self.ser.write((message + "\n").encode())
        else:
            print(message)

    def recv(self):
        if self.useSerial:
            return self.ser.readline().decode()
        else:
            return ""

    def recvUntilOk(self):
        msg = ""
        msgs = []
        while (msg != "ok\n"):
            if self.useSerial:
                msg = self.recv()
                msgs.append(msg)
            else:
                msg = "ok\n"
            print("RECV: " + msg, end='')
        print()
        return msgs