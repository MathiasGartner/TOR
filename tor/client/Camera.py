from picamera import PiCamera
from picamera.array import PiRGBArray
import time

class Camera:
    def __init__(self):
        self.cam = PiCamera(resolution=(2592, 1944))
        #self.cam.led = False
        self.cam.iso = 400
        time.sleep(2)
        self.cam.shutter_speed = 50000
        self.cam.exposure_mode = 'off'
        self.cam.contrast = 20
        self.cam.awb_mode = 'off'
        awbr = 1.2851
        awbb = 1.5781
        self.awb_gains = (awbr, awbb)

    def takePicture(self):
        rawCapture = PiRGBArray(self.cam)
        self.cam.capture(rawCapture, format="bgr")
        image = rawCapture.array
        return image

    def close(self):
        self.cam.close()
