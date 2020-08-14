import logging
log = logging.getLogger(__name__)

from picamera import PiCamera
from picamera.array import PiRGBArray
import time

import tor.client.ClientSettings as cs

class Camera:
    def __init__(self):
        self.cam = PiCamera(resolution=(2592, 1944))
        #self.cam.led = False
        self.cam.iso = cs.CAM_ISO
        time.sleep(2)
        self.cam.shutter_speed = cs.CAM_SHUTTER_SPEED
        self.cam.exposure_mode = 'off'
        self.cam.contrast = cs.CAM_CONTRAST
        self.cam.awb_mode = 'off'
        awbr = cs.CAM_AWBR
        awbb = cs.CAM_AWBB
        self.awb_gains = (awbr, awbb)

    def takePicture(self):
        rawCapture = PiRGBArray(self.cam)
        self.cam.capture(rawCapture, format="bgr")
        image = rawCapture.array
        return image

    def close(self):
        self.cam.close()
