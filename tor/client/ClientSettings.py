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

LX = 242
LY = 242
LZ = 290 - 15 + 0 #height - hook + empiric value...
LMAX = math.sqrt(LX**2 + LY**2 + LZ**2)

RAMP_FORBIDDEN_X_MIN = 50
RAMP_FORBIDDEN_X_MAX = LX - 50
RAMP_DROPOFF_Y = 0
RAMP_DROPOFF_Z = 0
RAMP_END_Y = 115
RAMP_END_Z = LZ - 65
RAMP_START_Z = 50
RAMP_ALPHA = np.arctan((RAMP_END_Z - RAMP_START_Z) / RAMP_END_Y)
MAGNET_RADIUS = 12
MAGNET_HEIGHT = 50
DICE_HEIGHT = 20
PICKUP_ABOVE_GROUND = DICE_HEIGHT
PICKUP_Z = LZ - MAGNET_HEIGHT - PICKUP_ABOVE_GROUND
BEFORE_PICKUP_POSITION = Position(LX/2, 200, 50)
AFTER_PICKUP_POSITION = Position(LX/2, 200, 50)
PARKING_POSITION = Position(LX/2, 200, 50)

PULSE_MAGNET_TIME_MS = 100
WAIT_BEFORE_ROLL_TIME = 1
DIE_ROLL_TIME = 1

#special positions
BOX_SIZE = Position(LX, LY, LZ)
CORNER_Z = Position(0, 0, 0)
CORNER_Y = Position(LX, 0, 0)
CORNER_X = Position(LX, LY, 0)
CORNER_E = Position(0, LY, 0)
CENTER_TOP = Position(LX/2, LY/2, 50) #use min_z for z coordinate
CENTER_BOTTOM = Position(LX/2, LY/2, PICKUP_Z)
#DROPOFF_ADVANCE_POSITION = Position(LX/2, 30, 30)
#DROPOFF_POSITION = Position(85, 8, 17)
DROPOFF_ADVANCE_POSITION = Position(60, 30, 30)
DROPOFF_POSITION = Position(60, 8, 11)
HOME_POSITION = CORNER_X
HOME_CORDS =  HOME_POSITION.toCordLengths()

#feedrates
FR_DEFAULT = 200
FR_FAST_MOVES = 450
FR_DROPOFF_ADVANCE = 50
FR_DROPOFF_ADVANCE_SLOW = 30
FR_SEARCH_BED = 200
FR_SEARCH_RAMP = 200

#Calibration meshpoints for bed, ramp and magnet
MESH_BED_TYPE = "B"
MESH_BED_DEFAULT = [(0, 242, 198),
                    (121, 242, 200),
                    (242, 242, 203),
                    (0, 150, 201),
                    (121, 150.5, 204),
                    (242, 150, 203)]
MESH_BED = np.array(MESH_BED_DEFAULT)
MESH_RAMP_TYPE = "R"
MESH_RAMP_DEFAULT = [(0, 130, 140),
                     (121, 130, 140),
                     (242, 130, 140),
                     (0, 40, 65),
                     (121, 40, 65),
                     (242, 40, 65)]
MESH_RAMP = np.array(MESH_RAMP_DEFAULT)
MESH_MAGNET_TYPE = "M"
MESH_MAGNET_DEFAULT = [(60, 20, 25),
                       (110, 20, 25),
                       (160, 20, 25),
                       (220, 20, 25)]
MESH_MAGNET = np.array(MESH_MAGNET_DEFAULT)

#camera settings
CAM_ISO = 400
CAM_SHUTTER_SPEED = 50000
CAM_CONTRAST = 20
CAM_AWBR = 1.2851
CAM_AWBB = 1.5781

# dice recognition configuration:
IMG_USE_WARPING = False
IMG_TL = [20, 420] # top left
IMG_BL = [20, 1675] # bottom left
IMG_TR = [2570, 420] # top right
IMG_BR = [2570, 1675] # bottom right
IMG_PX_X = 2592
IMG_PX_Y = 1944 #PiCameraResolutionRounded: frame size rounded up from 2592x1944 to 2592x1952. should I use 1952 here?

BLOB_MIN_DIAMETER = 18
BLOB_MAX_DIAMETER = 31

# movement configuration:
G_HOMING = "G28 A0 S50 P130 F68 R8 D1.05 B1.15"

# LED strip configuration:
LED_COUNT      = 81      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
#LED_BRIGHTNESS = 150     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LEDS_RIGHT = range(0, 20)
LEDS_BACK = range(21, 60)
LEDS_LEFT = range(61, 80)

# LED properties
LED_TOP_BRIGHTNESS = 150
LED_TOP_BRIGHTNESS_OFF = 0
LED_STRIP_BRIGHTNESS = 100
LED_STRIP_DEFAULT_COLOR = (20, 170, 20)

# properties of natural materials on ramp
RAMP_MATERIAL = "plain"
RAMP_MATERIAL_HEIGHT = 0

#options for die pickup
HOME_EVERY_N_RUNS = 5
HOME_AFTER_N_FAILS = 3
HOME_AFTER_N_SAME_RESULTS = 3
USE_IMAGE_RECOGNITION = True
SEARCH_RAMP = False
STORE_IMAGES = True
SHOW_DIE_RESULT_WITH_LEDS = False

#web pages directory
WEB_DIRECTORY = "/home/pi/tor/client/html"

#die paramters
DIE_SIZE_X=120
DIE_SIZE_Y=120

