import argparse
import cv2
import time
import numpy as np
import os

from tor.client import ClientSettings as cs
from tor.client.MovementManager import MovementManager
from tor.client.MovementRoutines import MovementRoutines
from tor.client.Position import Position
from tor.base.DieRecognizer import DieRecognizer
from tor.client.Camera import Camera
from tor.client.ClientManager import ClientManager
from tor.client.LedManager import LedManager

#################
### arguments ###
#################

parser = argparse.ArgumentParser()
parser.add_argument("-l", dest="led", action="store_true")
parser.add_argument("-pic", dest="take_picture", action="store_true")
parser.add_argument("-home", dest='doHoming', action="store_true")
parser.add_argument("-bed", dest='bed', action="store_true")
parser.add_argument("-ramp", dest='ramp', action="store_true")
parser.add_argument("-magnet", dest='magnet',action='store_true')
parser.add_argument("-camera", dest='camera', action="store_true")
parser.add_argument("-image", dest='image', action="store_true")
parser.add_argument("-p", dest="points", default=None, type=int)
args = parser.parse_args()

###########################
### get client identity ###
###########################

cm = ClientManager()
welcomeMessage = "I am client with ID {} and IP {}. My ramp is made out of {}, mounted on position {}"
print("#######################")
print(welcomeMessage.format(cm.clientId, cm.clientIdentity["IP"], cm.clientIdentity["Material"], cm.clientIdentity["Position"]))
print("#######################")

### load custom settings from file and server
ccsModuleName = "tor.client.CustomClientSettings." + cm.clientIdentity["Material"]
try:
    import importlib
    customClientSettings = importlib.import_module(ccsModuleName)
except:
    print("No CustomClientSettings found.")

cm.loadSettings()
cm.loadMeshpoints()

######################
### Initialization ###
######################

lm = LedManager()
mm = MovementManager()
mr = MovementRoutines()

def saveCurrentView(path):
    cam = Camera()
    dr = DieRecognizer()
    if (args.led):
        lm.setAllLeds()
    mm.setTopLed(cs.LED_TOP_BRIGHTNESS)
    image = cam.takePicture()
    cam.close()
    if (args.led):
        lm.clear()
    mm.setTopLed(cs.LED_TOP_BRIGHTNESS_OFF)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = dr.transformImage(image)
    dr.writeImage(image,"current_view.jpg", directory=path)

def calibrateMeshpoints(type, p, pointsToCalibrate=None):
    if pointsToCalibrate is None:
        pointsToCalibrate = range(len(p))
    elif not isinstance(pointsToCalibrate, list):
        pointsToCalibrate = [pointsToCalibrate]
    if type == "B" or type == "R":
        for i in pointsToCalibrate:
            finish = False
            while not finish:
                pos = Position(p[i, 0], p[i, 1], p[i, 2])
                if type == 'B' and i > 2:
                    mm.moveToPos(cs.BEFORE_PICKUP_POSITION,True)
                    mm.waitForMovementFinished()
                mm.moveToPos(pos, True)
                mm.waitForMovementFinished()
                if ((type == "B") and args.take_picture):
                    saveCurrentView(cs.WEB_DIRECTORY)
                    print("http://" + cm.clientIdentity["IP"])
                print('Position OK? (y/n)')
                if ((input() or 'y') == 'y'):
                    finish = True
                else:
                    print('Current position')
                    print(pos)
                    print('New position')
                    p[i, 0] = input('x:') or p[i, 0]
                    p[i, 1] = input('y:') or p[i, 1]
                    p[i, 2] = input('z:') or p[i, 2]
    elif type == "M":
        for i in pointsToCalibrate:
            print('Searching point', i + 1)
            finish = False
            while not finish:
                mm.moveToPos(Position(p[i, 0], p[i, 1] + 20, p[i, 2] + 20), True)
                mm.waitForMovementFinished()
                mm.setFeedratePercentage(30)
                mm.moveToPos(Position(p[i, 0], p[i, 1], p[i, 2]), True)
                mm.waitForMovementFinished()
                # mm.setFeedratePercentage(30)
                time.sleep(2)
                mm.rollDie()
                print('Position OK? (y/n/c)')
                answ = input() or 'y'
                if (answ == 'y'):
                    finish = True
                    cm.saveMeshpoints("M", p)
                    mm.setFeedratePercentage(200)
                    mm.moveToPos(Position(p[i, 0], p[i, 1] + 30, p[i, 2] + 20), True)
                    mm.waitForMovementFinished()
                    mr.pickupDie()
                    mm.waitForMovementFinished()
                elif (answ == 'n'):
                    print('Current position:', mm.currentPosition)
                    mm.moveToPos(Position(p[i, 0], p[i, 1] + 20, p[i, 2] + 20), True)
                    mm.waitForMovementFinished()
                    print('New position')
                    p[i, 0] = input('x:') or p[i, 0]
                    p[i, 1] = input('y:') or p[i, 1]
                    p[i, 2] = input('z:') or p[i, 2]
                else:
                    mm.doHoming()
                    mm.setFeedratePercentage(200)
                    mm.moveToPos(Position(120, 100, 50))
                    mm.waitForMovementFinished()
                    print(p[i, 0], p[i, 1], p[i, 2])
                    mm.setFeedratePercentage(50)
                    print('New position')
                    p[i, 0] = input('x:') or p[i, 0]
                    p[i, 1] = input('y:') or p[i, 1]
                    p[i, 2] = input('z:') or p[i, 2]
    else:
        print("mesh type " + type + " not known.")


###############
### Program ###
###############

if args.doHoming:
    homingOkay = False
    while not homingOkay:
        mm.doHoming()
        print('Homing OK? (y/n)')
        answ = input() or 'y'
        if answ == 'y':
            homingOkay = True

if args.bed:
    cm.loadMeshpoints()

    calibrateMeshpoints("B", cs.MESH_BED, args.points)
    cm.saveMeshpoints("B", cs.MESH_BED)

    if not args.ramp:
        mm.moveToPos(cs.PARKING_POSITION, True)
        exit(0)

if args.ramp:
    # overcome ramp
    mm.moveToPos(cs.AFTER_PICKUP_POSITION, True)
    mm.waitForMovementFinished()
    calibrateMeshpoints("R", cs.MESH_RAMP, args.points)
    cm.saveMeshpoints("R", cs.MESH_RAMP)

    mm.moveToPos(cs.PARKING_POSITION, True)
    exit(0)

if args.magnet:
    mm.setFeedratePercentage(300)
    mm.moveToPos(Position(120, 100, 100), True)
    mm.waitForMovementFinished()

    cm.loadMeshpoints()

    calibrateMeshpoints("M", cs.MESH_MAGNET, args.points)
    cm.saveMeshpoints("M", cs.MESH_MAGNET)

    exit(0)

if args.camera:
    finish = False
    dr = DieRecognizer()
    cm.loadSettings()
    lm.setAllLeds()
    mm.setTopLed(cs.LED_TOP_BRIGHTNESS)
    while not finish:
        cam = Camera()
        image = cam.takePicture()
        cam.close()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        dr.writeImage(image, "camera.jpg", directory=cs.WEB_DIRECTORY)
        print("http://" + cm.clientIdentity["IP"] + "/camera.html")
        print('Camera settings OK? (y/n)')
        answ = input() or 'y'
        if answ == "y":
            finish = True
            cm.saveCameraSettings()
        else:
            #print("current settings:", cs.CAM_ISO, cs.CAM_SHUTTER_SPEED, cs.CAM_CONTRAST, cs.CAM_AWBR, cs.CAM_AWBB)
            print("current settings:", cs.CAM_ISO, cs.CAM_SHUTTER_SPEED, cs.CAM_CONTRAST)
            cs.CAM_ISO = int(input("ISO {100,200,400,800}:") or cs.CAM_ISO)
            cs.CAM_SHUTTER_SPEED = int(input("Shutter [µs]:") or cs.CAM_SHUTTER_SPEED)
            cs.CAM_CONTRAST = int(input("contrast [-100,100]:") or cs.CAM_CONTRAST)
            #cs.CAM_AWBR = float(input("awbr [0.0,8.0]:") or cs.CAM_AWBR)
            #cs.CAM_AWBB = float(input("awbb [0.0,8.0]:") or cs.CAM_AWBB)
    lm.clear()
    mm.setTopLed(cs.LED_TOP_BRIGHTNESS_OFF)
    exit(0)

if args.image:
    #############
    # TL ### TR #
    # BL ### BR #
    #############
    ### RAMP  ###
    #############
    finish = False
    cm.loadSettings()
    needsWarping = cs.IMG_USE_WARPING
    tl = cs.IMG_TL
    bl = cs.IMG_BL
    tr = cs.IMG_TR
    br = cs.IMG_BR
    dr = DieRecognizer()
    while not finish:
        cam = Camera()
        if (args.led):
            lm.setAllLeds()
            mm.setTopLed(cs.LED_TOP_BRIGHTNESS)
        image = cam.takePicture()
        cam.close()
        if (args.led):
            lm.clear()
            mm.setTopLed(cs.LED_TOP_BRIGHTNESS_OFF)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if not needsWarping:
            transformedImage = dr.cropImage(image, tl, br)
            markedImage = dr.markCropLines(image, tl, br, isGray=True)
        else:
            dr.createWarpMatrix(tl, bl, tr, br)
            transformedImage = dr.warpImage(image)
            markedImage = dr.markLines(image, [[tl, tr], [tl, bl], [bl, br], [tr, br]], isGray=True)

        dr.writeImage(markedImage, "marked.jpg", directory=cs.WEB_DIRECTORY)
        dr.writeImage(transformedImage, "transformed.jpg", directory=cs.WEB_DIRECTORY)

        print("http://" + cm.clientIdentity["IP"] + "/image.html")
        if needsWarping:
            print("currently warping, use this only if really needed (processing time of ~1 second)")
        else:
            print("currently cropping, switch to warping only if really needed (processing time of ~1 second)")
        print('Image OK? (y/c/w/r) [yes/crop/warp/refresh]')
        answ = input() or 'y'
        if answ == "y":
            finish = True
            cs.IMG_USE_WARPING = needsWarping
            cs.IMG_TL = tl
            cs.IMG_BL = bl
            cs.IMG_TR = tr
            cs.IMG_BR = br
            if needsWarping:
                cm.saveImageSettingsWarping(tl, bl, tr, br)
            else:
                cm.saveImageSettingsCropping(tl, br)
        elif answ == "c":
            needsWarping = False
            print('Current top left:', tl)
            tl[0] = int(input("x:") or tl[0])
            tl[1] = int(input("y:") or tl[1])
            print('Current bottom right:', br)
            br[0] = int(input("x:") or br[0])
            br[1] = int(input("y:") or br[1])
        elif answ == "w":
            needsWarping = True
            print('Current top left:', tl)
            tl[0] = int(input("x:") or tl[0])
            tl[1] = int(input("y:") or tl[1])
            print('Current bottom left:', bl)
            bl[0] = int(input("x:") or bl[0])
            bl[1] = int(input("y:") or bl[1])
            print('Current top right:', tr)
            tr[0] = int(input("x:") or tr[0])
            tr[1] = int(input("y:") or tr[1])
            print('Current bottom right:', br)
            br[0] = int(input("x:") or br[0])
            br[1] = int(input("y:") or br[1])
        elif answ == "r":
            pass
    exit(0)
