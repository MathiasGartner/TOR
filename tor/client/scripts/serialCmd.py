#!/usr/bin/env python3

import serial
import sys

ser = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

cmd = sys.argv[1]
ser.write((cmd + "\n").encode())
msg = ""
while(msg != "ok\n"):
    msg = ser.readline().decode()
    print("RECV: " + msg, end='')
print()
