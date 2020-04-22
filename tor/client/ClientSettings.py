import math
import numpy as np
import sys

from tor.client.Position import Position

if sys.platform == "linux":
    ON_RASPI = True
else:
    ON_RASPI = False

LX = 246
LY = 246
LZ = 290 - 15 + 0 #height - hook + empiric value...
LMAX = math.sqrt(LX**2 + LY**2 + LZ**2)
BOX_SIZE = Position(LX, LY, LZ)
HOME_POSITION = Position(0, 0, 0)
HOME_CORDS =  HOME_POSITION.toCordLengths()
CORNER_X = Position(0, 0, 0)
CORNER_Y = Position(LX, 0, 0)
CORNER_Z = Position(LX, LY, 0)
CORNER_E = Position(0, LY, 0)

RAMP_FORBIDDEN_X_MIN = 30
RAMP_FORBIDDEN_X_MAX = LX - 30
RAMP_FOBIDDEN_Y = 20
RAMP_DROPOFF_Y = 0
RAMP_DROPOFF_Z = 0
RAMP_END_Y = 115
RAMP_END_Z = LZ - 65
RAMP_START_Z = 50
RAMP_ALPHA = np.arctan((RAMP_END_Z - RAMP_START_Z) / RAMP_END_Y)
MAGNET_RADIUS = 12
MAGNET_HEIGHT = 40
PICKUP_ABOVE_GROUND = 18
PICKUP_Z = LZ - MAGNET_HEIGHT - PICKUP_ABOVE_GROUND

DIE_ROLL_TIME = 2

IMAGE_CROP_X_LEFT = 10
IMAGE_CROP_X_RIGHT = 0
IMAGE_CROP_Y_TOP = 325
IMAGE_CROP_Y_BOTTOM = 247
IMAGE_PX_X = 2592
IMAGE_PX_Y = 1944

AREA_X = LX
AREA_Y = LY - RAMP_END_Y
AREA_PX_X = IMAGE_PX_X - IMAGE_CROP_X_LEFT - IMAGE_CROP_X_RIGHT
AREA_PX_Y = IMAGE_PX_Y - IMAGE_CROP_Y_TOP - IMAGE_CROP_Y_BOTTOM
AREA_PX_PER_MM_X = AREA_PX_X / AREA_X
AREA_PX_PER_MM_Y = AREA_PX_Y / AREA_Y

BLOB_MIN_DIAMETER = 18
BLOB_MAX_DIAMETER = 31