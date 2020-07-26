
import argparse

import tor.client.ClientSettings as cs

parser = argparse.ArgumentParser()
parser.add_argument("color", nargs='*', default=[255, 255, 255], type=int)
parser.add_argument("-b", dest="brightness", default=255, type=int)
parser.add_argument("-t", dest="topLed", action="store_true")
parser.add_argument("-s", dest="segment", default="RLB")
args = parser.parse_args()

if args.topLed:
    from tor.client.MovementManager import MovementManager
    mm = MovementManager()
    mm.setTopLed(args.brightness)
else:
    from tor.client.LedManager import LedManager
    lm = LedManager(args.brightness)
    r = args.color[0]
    g = args.color[1]
    b = args.color[2]
    if "L" in args.segment:
        leds = cs.LEDS_LEFT
        lm.setLeds(leds, r, g, b)
    if "R" in args.segment:
        leds = cs.LEDS_RIGHT
        lm.setLeds(leds, r, g, b)
    if "B" in args.segment:
        leds = cs.LEDS_BACK
        lm.setLeds(leds, r, g, b)
