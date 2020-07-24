
import argparse
import time

import tor.client.ClientSettings as cs
from tor.client.MovementManager import MovementManager
from tor.client.Position import Position
from tor.client.Cords import Cords

parser = argparse.ArgumentParser()
parser.add_argument("-l", dest="moveLeft", action="store_true")
parser.add_argument("-off", dest="motorOff", action="store_true")
parser.add_argument("-all", dest="all", action="store_true")
args = parser.parse_args()

def move(direction):
    mm.sendGCode("M17")
    zeroPos = Cords([0, 0, 0, 0])
    mm.setCurrentPosition(zeroPos)

    dest = 200 * direction
    pos = Cords([0, 0, dest, dest])
    mm.moveToCords(pos)


mm = MovementManager()
mm.initBoard()
time.sleep(0.5)
mm.setFeedratePercentage(500)

if args.all or not args.motorOff:
    move(1)

if args.moveLeft or args.all:
    move(-1)

if args.motorOff or args.all:
    mm.sendGCode("M18")
