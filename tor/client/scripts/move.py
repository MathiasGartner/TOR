
import argparse
import time

import tor.client.ClientSettings as cs
from tor.client.MovementManager import MovementManager
from tor.client.Position import Position

parser = argparse.ArgumentParser()
parser.add_argument("position", nargs='*', default=[cs.CENTER_TOP.x, cs.CENTER_TOP.y, cs.CENTER_TOP.z], type=float)
parser.add_argument("-f", dest="feedratePercentage", default=cs.FEEDRATE_PERCENTAGE, type=int)
parser.add_argument("-h", dest="doHoming", action="store_true")
args = parser.parse_args()

mm = MovementManager()
mm.initBoard()
time.sleep(0.5)

if args.feedratePercentage != cs.FEEDRATE_PERCENTAGE:
    mm.setFeedratePercentage(args.feedratePercentage)

if args.doHoming:
    mm.doHoming()

pos = Position(args.position[0], args.position[1], args.position[2])
if pos.isValid():
    mm.moveToPos(pos)
