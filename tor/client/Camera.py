from picamera import PiCamera
from picamera.array import PiRGBArray
import time

class Camera:
    def __init__(self):
        self.cam = PiCamera(resolution=(2592, 1944))
        #self.cam.led = False
        self.cam.iso = 300

    def takePicture(self):
        rawCapture = PiRGBArray(self.cam)
        self.cam.capture(rawCapture, format="bgr")
        image = rawCapture.array
        return image
