import math
import numpy as np
import sys

from tor.client.Position import Position

if sys.platform == "linux":
    ON_RASPI = True
else:
    ON_RASPI = False

L_X_RAW = 290
L_Y_RAW = 290
L_ANCHOR_Z_HOOK_X = 12
L_ANCHOR_Z_HOOK_Y = 15
L_ANCHOR_E_HOOK_X = 12
L_ANCHOR_E_HOOK_Y = 15

MIN_Z = 20

LX = 252
LY = LX
LZ = 290 - 15 + 0 #height - hook + empiric value...
LMAX = math.sqrt(LX**2 + LY**2 + LZ**2)

RAMP_FORBIDDEN_X_MIN = 50
RAMP_FORBIDDEN_X_MAX = LX - 50
RAMP_FOBIDDEN_Y = 20
RAMP_DROPOFF_Y = 0
RAMP_DROPOFF_Z = 0
RAMP_END_Y = 115
RAMP_END_Z = LZ - 65
RAMP_START_Z = 50
RAMP_ALPHA = np.arctan((RAMP_END_Z - RAMP_START_Z) / RAMP_END_Y)
MAGNET_RADIUS = 12
MAGNET_HEIGHT = 50
DICE_HEIGHT = 16
PICKUP_ABOVE_GROUND = DICE_HEIGHT + 3
PICKUP_Z = LZ - MAGNET_HEIGHT - PICKUP_ABOVE_GROUND

PULSE_MAGNET_TIME = 0.1
DIE_ROLL_TIME = 2

#special positions
BOX_SIZE = Position(LX, LY, LZ)
HOME_POSITION = Position(0, 0, 0)
HOME_CORDS =  HOME_POSITION.toCordLengths()
CORNER_X = Position(0, 0, 0)
CORNER_Y = Position(LX, 0, 0)
CORNER_Z = Position(LX, LY, 0)
CORNER_E = Position(0, LY, 0)
CENTER_TOP = Position(LX/2, LY/2, MIN_Z)
CENTER_BOTTOM = Position(LX/2, LY/2, PICKUP_Z)
DROPOFF_ADVANCE_POSITION = Position(LX/2, 20, 50)
DROPOFF_POSITION = Position(LX/2, 5, 30)

# dice recognition configuration:
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

# movement configuration:
FEEDRATE_PERCENTAGE = 250

# LED strip configuration:
LED_COUNT      = 144      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 150     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LEDS_RIGHT = range(0, 22)
LEDS_BACK = range(23, 66)
LEDS_LEFT = range(67, 88)
LEDS_FRONT = range(89, LED_COUNT)