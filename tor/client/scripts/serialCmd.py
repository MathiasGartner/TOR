#!/usr/bin/env python3

import serial
import sys

ser = serial.Serial(
    #port='/dev/ttyS0', #serial connection via RX and TX pins
    port="/dev/ttyACM0", #serial connectin via USB
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=10
)

cmd = sys.argv[1]
ser.write((cmd + "\n").encode())
waitForResponse = True
if cmd == "M997": #reflash firmware
    waitForResponse = False
closeOnOk = True
if len(sys.argv) > 2:
    closeOnOk = False
if waitForResponse:
    msg = ""
    while(not (msg == "ok\n" and closeOnOk)):
        msg = ser.readline().decode()
        print("RECV: " + msg, end='')
    print()
