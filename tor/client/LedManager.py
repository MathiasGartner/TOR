import logging
log = logging.getLogger(__name__)

import time

import tor.client.ClientSettings as cs
from tor.base.utils import Utils

if cs.ON_RASPI:
    from rpi_ws281x import Adafruit_NeoPixel, Color

class LedManager:
    def __init__(self, brightness=None):
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

    def getColorFromTuple(self, rgb):
        return Color(rgb[0], rgb[1], rgb[2])

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

    def testWheel(self, pos):
        # from https://github.com/jgarff/rpi_ws281x/blob/master/python/examples/strandtest.py
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)

    def testTheaterChaseRainbow(self, wait_ms=50):
        # from https://github.com/jgarff/rpi_ws281x/blob/master/python/examples/strandtest.py
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, self.testWheel((i + j) % 255))
                self.strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, 0)

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

    def loadUserMode(self):
        col = self.getColorFromTuple(cs.USER_LOAD_COLOR)
        self.clear()
        time.sleep(0.3)
        for i in range(self.strip.numPixels(), 0, -1):
            self.strip.setPixelColor(i, col)
            time.sleep(0.1)
            self.strip.show()
        self.blink(blinkTime=0.6, col=col)

    def unloadUserMode(self):
        col = self.getColorFromTuple(cs.USER_LOAD_COLOR)
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, self.OFF_COLOR)
            time.sleep(0.1)
            self.strip.show()

    def showResult(self, result):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, self.R if (i < result*self.strip.numPixels()/6.) else self.OFF_COLOR)
        self.strip.show()

    def setLeds(self, leds, r, g, b):
        for i in leds:
            self.strip.setPixelColor(i, Color(r, g, b))
        self.strip.show()

    def setAllLeds(self, color=None, r=None, g=None, b=None):
        if color is None:
            color = self.DEFAULT_COLOR
        if r is not None and g is not None and b is not None:
            color = Color(Utils.clamp255(r), Utils.clamp255(g), Utils.clamp255(b))
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
        self.strip.show()

    def blink(self, blinkTime=0.01, col=None, repeat=3, keepLight=True):
        if col is None:
            col = self.W
        for i in range(repeat):
            self.setAllLeds(col)
            time.sleep(blinkTime)
            self.clear()
            time.sleep(blinkTime)
        if keepLight:
            self.setAllLeds(col)

