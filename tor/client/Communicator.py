import logging
log = logging.getLogger(__name__)
logSerial = logging.getLogger("serial")

import serial
import threading
import time

from tor.base.Singleton import Singleton
import tor.client.ClientSettings as cs

class Communicator(Singleton):
    def __init__(self, serialPort = ""):
        if hasattr(self, "_initialized") and self._initialized:
            log.warning("wanted to initialize Communicator again")
            return
        self._initialized = True

        self._lock = threading.Lock()
        if serialPort == "":
            if cs.ON_RASPI:
                serialPort = "/dev/ttyACM0"
                #serialPort = "/dev/ttyS0"
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

    def close(self):
        if self.useSerial:
            with self._lock:
                self.ser.close()

    def send(self, message):
        if self.useSerial:
            with self._lock:
                logSerial.debug(f"SEND: {message}")
                self.ser.write((message + "\n").encode())
        else:
            logSerial.debug(message)

    def recv(self):
        if self.useSerial:
            with self._lock:
                return self.ser.readline().decode()
        else:
            return ""

    def recvUntilOk(self, timeout=60):
        #TODO: implement option for timeout when waiting for "ok" message
        msg = ""
        msgs = []
        start_time = time.time()
        with self._lock:
            while (msg != "ok\n"):
                if time.time() - start_time > timeout:
                    logSerial.warning("recvUntilOk() timed out")
                    break
                if self.useSerial:
                    msg = self.ser.readline().decode()
                    msgs.append(msg)
                else:
                    msg = "ok\n"
                logSerial.debug(f"RECV: {msg}")
        return msgs