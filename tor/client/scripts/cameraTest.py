
import cv2
import numpy as np
import time

from picamera import PiCamera
from picamera.array import PiRGBArray

camera = PiCamera(resolution=(2592, 1944), framerate = 2)

iso = [100, 200, 400, 800]
shutter = range(20000, 100001, 20000)
contrast = range(0, 81, 10)

for i in iso:
    camera.iso = i
    time.sleep(2)

    for s in shutter:
        camera.shutter_speed = s
        camera.exposure_mode = 'off'

        for c in contrast:
            camera.contrast = c

            camera.awb_mode = 'off'
            awbr = 1.2851
            awbb = 1.5781
            camera.awb_gains = (awbr, awbb)
            filename_raw = 'iso={}_shutter={}_contrast={}.{}'
            filename = filename_raw.format(i, s, c, "{}")
            print(filename)

            #camera.capture(filename)
            rawCapture = PiRGBArray(camera)
            camera.capture(rawCapture, format="bgr")
            image = rawCapture.array
            cv2.imwrite(filename.format("jpg"), image)
            np.save(filename.format("npy"), image)