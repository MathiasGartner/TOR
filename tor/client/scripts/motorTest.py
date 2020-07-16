
import argparse
import time

import tor.client.ClientSettings as cs
from tor.client.MovementManager import MovementManager
from tor.client.Position import Position
from tor.client.Cords import Cords

parser = argparse.ArgumentParser()
parser.add_argument("-l", dest="moveLeft", action="store_true")
parser.add_argument("-off", dest="motorOff", action="store_true")
args = parser.parse_args()

mm = MovementManager()
mm.initBoard()
time.sleep(0.5)

if args.motorOff:
    mm.sendGCode("M18")

else:
    mm.sendGCode("M17")
    zeroPos = Cords([0, 0, 0, 0])
    mm.setCurrentPosition(zeroPos)

    dest = 400 * (-1 if args.moveLeft else 1)
    pos = Cords([0, 0, dest, dest])
    mm.moveToCords(pos)
