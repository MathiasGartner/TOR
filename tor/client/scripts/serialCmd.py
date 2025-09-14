#!/usr/bin/env python3

import sys

from tor.client.Communicator import Communicator

com = Communicator()
com.ser.timeout = 10

cmd = sys.argv[1]
com.ser.write((cmd + "\n").encode())
waitForResponse = True
if cmd == "M997": #reflash firmware
    waitForResponse = False
closeOnOk = True
if len(sys.argv) > 2:
    closeOnOk = False
if waitForResponse:
    msg = ""
    while(not (msg == "ok\n" and closeOnOk)):
        msg = com.ser.readline().decode()
        print("RECV: " + msg, end='')
    print()
