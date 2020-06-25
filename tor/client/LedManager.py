import time

import tor.client.ClientSettings as cs

class LedManager:
    def __init__(self, brightness=cs.LED_BRIGHTNESS):
        from rpi_ws281x import Adafruit_NeoPixel, Color
        self.strip = Adafruit_NeoPixel(cs.LED_COUNT, cs.LED_PIN, cs.LED_FREQ_HZ, cs.LED_DMA, cs.LED_INVERT, brightness, cs.LED_CHANNEL)
        self.strip.begin()
        self.col_off = Color(0, 0, 0)
        self.G = Color(255, 0, 0)
        self.R = Color(0, 255, 0)
        self.B = Color(0, 0, 255)
        self.W = Color(255, 255, 255)

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
            self.strip.setPixelColor(i, self.col_off)
        self.strip.show()

    def showResult(self, result):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, self.R if (i < result) else self.col_off)
        self.strip.show()

    def setLeds(self, leds, r, g, b):
        from rpi_ws281x import Color
        for i in leds:
            self.strip.setPixelColor(i, Color(r, g, b))
        self.strip.show()
