import logging
log = logging.getLogger(__name__)

import math
import numpy as np
import os
import platform
import sys

from tor.client.Position import Position

if sys.platform == "linux" and platform.platform() == "Linux-4.19.118+-armv6l-with-debian-10.4":
    ON_RASPI = True
else:
    ON_RASPI = False

TOR_MARLIN_VERSION = "1.3"

#logging
LOG_LEVEL = logging.INFO
#LOG_LEVEL = logging.DEBUG

L_X_RAW = 290
L_Y_RAW = 290
L_ANCHOR_Z_HOOK_X = 12
L_ANCHOR_Z_HOOK_Y = 15
L_ANCHOR_E_HOOK_X = 12
L_ANCHOR_E_HOOK_Y = 15

MIN_Z = 30

LX = 249 #TOR_ANCHOR_X_E0 in tor-marlin
LY = 249 #TOR_ANCHOR_X_Y in tor-marlin
LZ = 290 - 15 + 0 #height - hook + empiric value..
LMAX = math.sqrt(LX**2 + LY**2 + LZ**2)

RAMP_FORBIDDEN_X_MIN = 50
RAMP_FORBIDDEN_X_MAX = LX - 50
RAMP_DROPOFF_Y = 0
RAMP_DROPOFF_Z = 0
RAMP_END_Y = 160#115
RAMP_END_Z = LZ - 65
RAMP_START_Z = 50
RAMP_ALPHA = np.arctan((RAMP_END_Z - RAMP_START_Z) / RAMP_END_Y)
MAGNET_RADIUS = 12
MAGNET_HEIGHT = 50
DICE_HEIGHT = 20
PICKUP_ABOVE_GROUND = DICE_HEIGHT
PICKUP_Z = LZ - MAGNET_HEIGHT - PICKUP_ABOVE_GROUND
AFTER_HOMING_POSITION = Position(230, 230, 30)
BEFORE_PICKUP_POSITION = Position(LX/2, 200, 50)
AFTER_PICKUP_POSITION = Position(LX/2, 200, 50)
PARKING_POSITION = Position(LX/2, LY/2, 50)
DEEP_PARKING_POSITION = Position(LX/2, LY/2, 100)

PULSE_MAGNET_TIME_MS = 100
WAIT_BEFORE_ROLL_TIME = 0.3
DIE_ROLL_TIME = 2
WAIT_ON_PICKUP_POS = 0.2
EXTRA_Z_FOR_PICKUP = 1.0
WAIT_BEFORE_TAKE_PICTURE_WHILE_HOMING = 1
WAIT_BEFORE_DISABLE_STEPPER_TIME = 0.1

USE_LEFT_DROPOFF_REGION = True
USE_RIGHT_DROPOFF_REGION = True

#cord correction for increasing pulley radius
PULLEY_RADIUS = 7.25
CORD_THICKNESS = 0.22
CORD_LAYERS_ON_PULLEY = 6.0
PULLEY_RADIUS_SQR = PULLEY_RADIUS * PULLEY_RADIUS
PULLEY_RADIUS_2PI = 2 * math.pi * PULLEY_RADIUS
CORD_THICKNESS_EFFECTIVE = CORD_THICKNESS / CORD_LAYERS_ON_PULLEY
CORD_THICKNESS_EFFECTIVE_PI = CORD_THICKNESS_EFFECTIVE * math.pi
CORD_THICKNESS_EFFECTIVE_SQR = CORD_THICKNESS_EFFECTIVE * CORD_THICKNESS_EFFECTIVE
PULLEY_RADIUS_OVER_CORD_THICKNESS_EFFECTIVE = PULLEY_RADIUS / CORD_THICKNESS_EFFECTIVE
PULLEY_RADIUS_OVER_CORD_THICKNESS_EFFECTIVE_SQR = PULLEY_RADIUS_OVER_CORD_THICKNESS_EFFECTIVE * PULLEY_RADIUS_OVER_CORD_THICKNESS_EFFECTIVE

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
DROPOFF_ADVANCE_OFFSET_Y = 20
DROPOFF_ADVANCE_OFFSET_Z = 20
DROPOFF_ADVANCE_OFFSET_Y2 = 10
DROPOFF_ADVANCE_OFFSET_Z2 = 10
DROPOFF_ADVANCE_Z = 50
HOME_POSITION = CORNER_X
RAMP_CRITICAL_Y = 170

#feedrates
FR_FACTOR = 1.0
FR_DEFAULT = int(200 * FR_FACTOR)
FR_SLOW_MOVE = int(130 * FR_FACTOR)
FR_FAST_MOVES = int(400 * FR_FACTOR)
FR_DROPOFF_ADVANCE = int(50 * FR_FACTOR)
FR_DROPOFF_ADVANCE_SLOW = int(30 * FR_FACTOR)
FR_SEARCH_BED = int(200 * FR_FACTOR)
FR_SEARCH_RAMP = int(200 * FR_FACTOR)

#Calibration meshpoints for bed, ramp and magnet
MESH_BED_TYPE = "B"
MESH_BED_DEFAULT = np.array([(0.0, LY, 205),
                             (LX/2, LY, 205),
                             (LX, LY, 205),
                             (0, 160, 205),
                             (LX/2, 160, 205),
                             (LX, 160, 205)])
MESH_BED = np.array(MESH_BED_DEFAULT)
MESH_RAMP_TYPE = "R"
MESH_RAMP_DEFAULT = np.array([(0.0, 130, 120),
                              (LX/2, 130, 120),
                              (LX, 130, 120),
                              (0, 40, 60),
                              (LX/2, 40, 60),
                              (LX, 40, 60)])
MESH_RAMP = np.array(MESH_RAMP_DEFAULT)
MESH_MAGNET_TYPE = "M"
MESH_MAGNET_DEFAULT = np.array([(60.0, 5, 30),
                                (105, 5, 30),
                                (LX-105, 5, 30),
                               (LX-60, 5, 30)])
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

BLOB_MIN_DIAMETER = 20 #18
BLOB_MAX_DIAMETER = 31

FAKE_BLOB_POSITIONS = []

# movement configuration:
G_HOMING = "G28 N{} A0 S50 P130 F68 R8 D1.05 B1.15"

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
LED_STRIP_BRIGHTNESS = 95
LED_STRIP_DEFAULT_COLOR = (40, 140, 120)

# properties of natural materials on ramp
RAMP_MATERIAL = "plain"
RAMP_MATERIAL_HEIGHT = 0

#options for die pickup
HOME_EVERY_N_RUNS = 50
HOME_AFTER_N_FAILS = 2
HOME_AFTER_N_SAME_RESULTS = 3
SAME_RESULT_NEAR_THRESHOLD_X = 20
USE_IMAGE_RECOGNITION = True
SEARCH_RAMP = False
STORE_IMAGES = False
STORE_IMAGES_NOT_FOUND = True
ALWAYS_MARK_DIE_ON_IMAGE = False
SHOW_DIE_RESULT_WITH_LEDS = False

# directories
WEB_DIRECTORY = "/home/pi/tor/client/html"
IMAGE_DIRECTORY = "/home/pi/pictures"
IMAGE_DIRECTORY_POSITION = IMAGE_DIRECTORY + "/positions"
IMAGE_DIRECTORY_DICE = IMAGE_DIRECTORY + "/dice"

#die paramters
DIE_SIZE_X=120
DIE_SIZE_Y=260

#CRITICAL AREA APPROACH
CRITICAL_AREA_APPROACH_Y=15
CRITICAL_AREA_APPROACH_Z=10

#APPROACH MAGNET
USE_MAGNET_BETWEEN_P0P1 = True
USE_MAGNET_BETWEEN_P2P3 = True
ALWAYS_USE_PX = -1

#USER ACTIONS
USER_LOAD_COLOR = (140, 40, 120)
EXIT_USER_MODE_AFTER_N_SECONDS = 60

#MISC
ASK_EVERY_NTH_SECOND_FOR_JOB_USERMODE = 0.15
ASK_EVERY_NTH_SECOND_FOR_JOB = 3
STANDARD_CLIENT_SLEEP_TIME = 5
UPDATE_ISACTIVE_SLEEP_TIME = 10

#MAGNET POSITION VERIFICATION
VERIFY_MAGNET_POSITION = Position(LX/2, 220, 185)
VERIFY_MAGNET_IMAGE_SIZE = 900
VERIFY_MAGNET_IMAGE_SIZE_SMALL = 30
VERIFY_MAGNET_IMAGE_TL = [830, 20]
VERIFY_MAGNET_IMAGE_BR = [px + VERIFY_MAGNET_IMAGE_SIZE for px in VERIFY_MAGNET_IMAGE_TL]