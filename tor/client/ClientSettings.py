import math
import numpy as np

from tor.client.Position import Position

LX = 190
LY = 190
LZ = 210
LMAX = math.sqrt(LX**2 + LY**2 + LZ**2)
BOX_SIZE = Position(LX, LY, LZ)

RAMP_DROPOFF_X = 0
RAMP_DROPOFF_Z = 0
RAMP_END_X = 100
RAMP_END_Z = LZ - 30
RAMP_START_Z = 20
RAMP_ALPHA = np.arctan((RAMP_END_Z - RAMP_START_Z) / RAMP_END_X)
PICKUP_Z = 200
MAGNET_RADIUS = 12
HOME_POSITION = Position(0, 0, 0)
HOME_CORDS =  HOME_POSITION.toCordLengths()