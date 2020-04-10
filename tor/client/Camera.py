from picamera import PiCamera
from picamera.array import PiRGBArray
import time

class Camera:
    def __init__(self):
        self.cam = PiCamera()
        rawCapture = PiRGBArray(self.cam)
        #self.cam.led = False

    def takePicture(self):
        camera.capture(rawCapture, format="bgr")
        image = rawCapture.array
        return image
