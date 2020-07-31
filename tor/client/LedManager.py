import logging
log = logging.getLogger(__name__)

import time

import tor.client.ClientSettings as cs

class LedManager:
    def __init__(self, brightness=None):
        from rpi_ws281x import Adafruit_NeoPixel, Color
        if brightness == None:
            brightness = cs.LED_STRIP_BRIGHTNESS
        if brightness < 0:
            brightness = 0
        elif brightness > 255:
            brightness = 255
        self.strip = Adafruit_NeoPixel(cs.LED_COUNT, cs.LED_PIN, cs.LED_FREQ_HZ, cs.LED_DMA, cs.LED_INVERT, brightness, cs.LED_CHANNEL)
        self.strip.begin()
        self.OFF_COLOR = Color(0, 0, 0)
        self.R = Color(255, 0, 0)
        self.G = Color(0, 255, 0)
        self.B = Color(0, 0, 255)
        self.W = Color(255, 255, 255)
        self.DEFAULT_COLOR = Color(cs.LED_STRIP_DEFAULT_COLOR[0], cs.LED_STRIP_DEFAULT_COLOR[1], cs.LED_STRIP_DEFAULT_COLOR[2])

    def test(self):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, self.R)
        self.strip.show()
        time.sleep(1)
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, self.G)
        self.strip.show()
        time.sleep(1)
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, self.B)
        self.strip.show()
        time.sleep(1)
        self.clear()

    def testRightLeftBack(self):
        for i in cs.LEDS_RIGHT:
            self.strip.setPixelColor(i, self.R)
        self.strip.show()
        time.sleep(1)
        for i in cs.LEDS_BACK:
            self.strip.setPixelColor(i, self.G)
        self.strip.show()
        time.sleep(1)
        for i in cs.LEDS_LEFT:
            self.strip.setPixelColor(i, self.B)
        self.strip.show()
        time.sleep(1)
        for i in cs.LEDS_BEFORE:
            self.strip.setPixelColor(i, self.W)
        self.strip.show()
        time.sleep(1)
        for i in cs.LEDS_AFTER:
            self.strip.setPixelColor(i, self.W)
        self.strip.show()
        time.sleep(1)

    def clear(self):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, self.OFF_COLOR)
        self.strip.show()

    def showResult(self, result):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, self.R if (i < result*self.strip.numPixels()/6.) else self.OFF_COLOR)
        self.strip.show()

    def setLeds(self, leds, r, g, b):
        from rpi_ws281x import Color
        for i in leds:
            self.strip.setPixelColor(i, Color(r, g, b))
        self.strip.show()

    def setAllLeds(self):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, self.DEFAULT_COLOR)
        self.strip.show()
