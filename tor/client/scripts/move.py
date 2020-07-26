import argparse
import cv2
import time
import numpy as np
import os

from tor.client import ClientSettings as cs
from tor.client.MovementManager import MovementManager
from tor.client.Position import Position
from tor.base.DieRecognizer import DieRecognizer
from tor.client.Camera import Camera
from tor.client.ClientManager import ClientManager
from tor.client.LedManager import LedManager


#################
### arguments ###
#################

parser = argparse.ArgumentParser()
parser.add_argument("position", nargs='*', default=[cs.CENTER_TOP.x, cs.CENTER_TOP.y, cs.CENTER_TOP.z], type=float)
parser.add_argument("-f", dest="feedratePercentage", default=cs.FEEDRATE_PERCENTAGE, type=int)
parser.add_argument("-c", dest="doHoming", action="store_true")
parser.add_argument("-l", dest="led", action="store_true")
parser.add_argument("-p", dest="take_picture", action="store_true")
parser.add_argument("-s", dest="segmented", action="store_true")
parser.add_argument("-start", dest='start', action="store_true")
parser.add_argument("-find", dest='find', action="store_true")
parser.add_argument("-points", dest='points', action="store_true")
parser.add_argument("-infinity", dest='infinity', action="store_true")
parser.add_argument("-spoints", dest='spoints',action='store_true') #validate starting points
parser.add_argument("-cor", dest="cal_on_run", default=0, type=int)
parser.add_argument("-camera", dest='camera', action="store_true")
parser.add_argument("-image", dest='image', action="store_true")
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
meshBed, meshRamp, meshMagnet = cm.getMeshpoints()

mm = MovementManager()
lm = LedManager()
mm.initBoard()
time.sleep(0.5)

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
    image = dr.transformImage(image)
    dr.writeImage(image,"current_view.jpg", directory=path)

def find_die():
    found = False
    result = -1
    if (cs.TRY_FINDING):
        cam = Camera()
        mm.setTopLed(cs.LED_TOP_BRIGHTNESS)
        image = cam.takePicture()
        mm.setTopLed(cs.LED_TOP_BRIGHTNESS_OFF)
        cam.close()

        dr = DieRecognizer()
        found, diePosition, result, processedImages = dr.getDiePosition(image, returnOriginalImg=True)
        directory = "found" if found else "fail"
        dr.writeImage(processedImages[0], directory=directory)
        dr.writeRGBArray(processedImages[0], directory=directory)
        print(result)
    if (found):
        if (args.led):  lm.showResult(result)
        print(diePosition)
        mm.setFeedratePercentage(300)
        mm.moveToPos(cs.BEFORE_PICKUP_POSITION,True)
        mm.waitForMovementFinished()
        #print('Position trafo')
        print(diePosition)
        #px=1.*diePosition.x/cs.LX
        #ylim_ramp=155
        #py=(1.*diePosition.y-ylim_ramp)/(cs.LY-ylim_ramp)
        print(co_trafo(diePosition.x,diePosition.y))
        mm.moveToPos(co_trafo(diePosition.x, diePosition.y), True)
        #mm.moveToPos(Position(min(diePosition.x , 241), diePosition.y, cs.PICKUP_Z), True)
        mm.waitForMovementFinished()
        mm.moveToPos(cs.AFTER_PICKUP_POSITION,True)
        mm.waitForMovementFinished()
    else:
        print('Die not found')
        search_die()
    return found,result

def load_pts():
    return np.concatenate((meshBed, meshRamp))

def co_trafo(px,py):
    p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12 = load_pts()
    if (px < 0.5):
        x = (1-py)*(p4[0]+px*(p6[0]-p4[0]))+py*(p1[0]+px*(p3[0]-p1[0]))
        y = (1-2*px)*(p4[1]+py*(p1[1]-p4[1]))+2*px*(p5[1]+py*(p2[1]-p5[1]))
        z = (1-2*px)*((1-py)*p4[2]+py*p1[2])+2*px*((1-py)*p5[2]+py*p2[2])
    else:
        x = (1-py)*(p6[0]+(1-px)*(p4[0]-p6[0]))+py*(p3[0]+(1-px)*(p1[0]-p3[0]))
        y = 2*(1-px)*(p5[1]+py*(p2[1]-p5[1]))+(2*px-1)*(p6[1]+py*(p3[1]-p6[1]))
        z = 2*(1-px)*((1-py)*p5[2]+py*p2[2])+(2*px-1)*((1-py)*p6[2]+py*p3[2])
    if (px < 0 or px > 1 or py < -0.1 or py > 1):
        print('Out of range!:', x, y, z)
        return Position(100, 100, 100)
    return Position(x, y, z)

def search_die():
    #starting position
    '''
    1  2  3
    4  5  6
    --------
    7  8  9
    10 11 12
    M      M
    '''
    p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12 = load_pts()
    n_rows=4 # rows per area
    ramp=False # Does ramp need search?
    mm.moveToPos(Position(p1[0],p1[1], 100),True)
    mm.waitForMovementFinished()
    mm.moveToPos(Position(p1[0],p1[1], p1[2]))
    mm.waitForMovementFinished()
    #raster bottom
    # mesh left side
    x_mesh_l=np.linspace(p1[0],p4[0],n_rows)
    y_mesh_l=np.linspace(p1[1],p4[1],n_rows)
    z_mesh_l=np.linspace(p1[2],p4[2],n_rows)
    #mesh center
    x_mesh_c = np.linspace(p2[0], p5[0], n_rows)
    y_mesh_c = np.linspace(p2[1], p5[1], n_rows)
    z_mesh_c = np.linspace(p2[2], p5[2], n_rows)
    #mesh right side
    x_mesh_r = np.linspace(p3[0], p6[0], n_rows)
    y_mesh_r = np.linspace(p3[1], p6[1], n_rows)
    z_mesh_r = np.linspace(p3[2], p6[2], n_rows)
    mm.setFeedratePercentage(200)
    for i in range(n_rows):
        if(np.mod(i,2)==0):
            mm.moveToPos(Position(x_mesh_l[i], y_mesh_l[i], z_mesh_l[i]), True)
            mm.waitForMovementFinished()
            mm.moveToPos(Position(x_mesh_c[i], y_mesh_c[i], z_mesh_c[i]), True)
            mm.waitForMovementFinished()
            mm.moveToPos(Position(x_mesh_r[i], y_mesh_r[i], z_mesh_r[i]), True)
            mm.waitForMovementFinished()
        if(np.mod(i,2)==1):
            mm.moveToPos(Position(x_mesh_r[i], y_mesh_r[i], z_mesh_r[i]), True)
            mm.waitForMovementFinished()
            mm.moveToPos(Position(x_mesh_c[i], y_mesh_c[i], z_mesh_c[i]), True)
            mm.waitForMovementFinished()
            mm.moveToPos(Position(x_mesh_l[i], y_mesh_l[i], z_mesh_l[i]), True)
            mm.waitForMovementFinished()

    ####ramp###
    if(ramp):
        cur_po = mm.getCurrentPosition()
        mm.moveToPos(Position(cur_po.x, cur_po.y+20, 100), True)
        mm.waitForMovementFinished()

        # mesh left side
        x_mesh_l=np.linspace(p7[0],p10[0],n_rows)
        y_mesh_l=np.linspace(p7[1],p10[1],n_rows)
        z_mesh_l=np.linspace(p7[2],p10[2],n_rows)
        #mesh center
        x_mesh_c = np.linspace(p8[0], p11[0], n_rows)
        y_mesh_c = np.linspace(p8[1], p11[1], n_rows)
        z_mesh_c = np.linspace(p8[2], p11[2], n_rows)
        #mesh right side
        x_mesh_r=np.linspace(p9[0], p12[0], n_rows)
        y_mesh_r = np.linspace(p9[1], p12[1], n_rows)
        z_mesh_r = np.linspace(p9[2], p12[2], n_rows)
        for i in range(n_rows):
            if(np.mod(i,2)==0):
                mm.moveToPos(Position(x_mesh_l[i], y_mesh_l[i], z_mesh_l[i]), True)
                mm.waitForMovementFinished()
                mm.moveToPos(Position(x_mesh_c[i], y_mesh_c[i], z_mesh_c[i]), True)
                mm.waitForMovementFinished()
                mm.moveToPos(Position(x_mesh_r[i], y_mesh_r[i], z_mesh_r[i]), True)
                mm.waitForMovementFinished()
            if(np.mod(i,2)==1):
                mm.moveToPos(Position(x_mesh_r[i], y_mesh_r[i], z_mesh_r[i]), True)
                mm.waitForMovementFinished()
                mm.moveToPos(Position(x_mesh_c[i], y_mesh_c[i], z_mesh_c[i]), True)
                mm.waitForMovementFinished()
                mm.moveToPos(Position(x_mesh_l[i], y_mesh_l[i], z_mesh_l[i]), True)
                mm.waitForMovementFinished()
    mm.setFeedratePercentage(250)
    mm.moveToPos(Position(100,200,100),True)

def start_script():
    spos = meshMagnet[np.random.randint(0, 4), :]
    mm.waitForMovementFinished()
    mm.moveToPos(Position(spos[0], spos[1]+20, 50), True)
    mm.waitForMovementFinished()
    mm.setFeedratePercentage(50)
    mm.moveToPos(Position(spos[0], spos[1]+10, spos[2]+10), True)
    mm.waitForMovementFinished()
    mm.setFeedratePercentage(30)
    mm.moveToPos(Position(spos[0], spos[1], spos[2]), True)
    mm.waitForMovementFinished()
    mm.setFeedratePercentage(450)
    time.sleep(1)
    mm.rollDie()
    if (args.find):
        time.sleep(2)
        found,result=find_die()
        return found,result

def loadMeshpoints():
    meshBed, meshRamp, meshMagnet = cm.getMeshpoints()

def calibrateMeshpoints(type, p):
    if type == "B" or type == "R":
        for i in range(len(p)):
            searching = True
            while (searching):
                pos = Position(p[i, 0], p[i, 1], p[i, 2])
                mm.moveToPos(pos, True)
                mm.waitForMovementFinished()
                if ((type == "B") and args.take_picture):
                    saveCurrentView('/var/www/html')
                    print("http://" + cm.clientIdentity["IP"])
                print('Position OK? (y/n)')
                if ((input() or 'y') == 'y'):
                    searching = False
                else:
                    print('Current position')
                    print(pos)
                    print('New position')
                    p[i, 0] = input('x:') or p[i, 0]
                    p[i, 1] = input('y:') or p[i, 1]
                    p[i, 2] = input('z:') or p[i, 2]
    elif type == "M":
        for i in range(len(p)):
            print('Searching point', i + 1)
            searching = True
            while (searching):
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
                    searching = False
                    mm.setFeedratePercentage(200)
                    mm.moveToPos(Position(p[i, 0], p[i, 1] + 30, p[i, 2] + 20), True)
                    mm.waitForMovementFinished()
                    find_die()
                    mm.waitForMovementFinished()
                elif (answ == 'n'):
                    print('Current position')
                    print(mm.getCurrentPosition())
                    mm.moveToPos(Position(p[i, 0], p[i, 1] + 20, p[i, 2] + 20), True)
                    mm.waitForMovementFinished()
                    print('New position')
                    p[i, 0] = input('x:') or p[i, 0]
                    p[i, 1] = input('y:') or p[i, 1]
                    p[i, 2] = input('z:') or p[i, 2]
                else:
                    mm.doHoming()
                    mm.setFeedratePercentage(400)
                    mm.moveToPos(Position(120, 100, 50), True)
                    mm.waitForMovementFinished()
                    print(p[i, 0], p[i, 1], p[i, 2])
                    mm.setFeedratePercentage(50)
                    print('New position')
                    p[i, 0] = input('x:') or p[i, 0]
                    p[i, 1] = input('y:') or p[i, 1]
                    p[i, 2] = input('z:') or p[i, 2]
    else:
        print("mesh type " + type + " not known.")

if args.points:
    loadMeshpoints()

    calibrateMeshpoints("B", meshBed)
    cm.saveMeshpoints("B", meshBed)

    # overcome ramp
    mm.moveToPos(Position(meshBed[5, 0], meshBed[5, 1]+30, 180), True)
    mm.moveToPos(Position(meshBed[5, 0], meshBed[5, 1], 60), True)
    mm.waitForMovementFinished()
    calibrateMeshpoints("R", meshRamp)
    cm.saveMeshpoints("R", meshRamp)

    exit(0)

if args.spoints:
    mm.setFeedratePercentage(300)
    mm.moveToPos(Position(120, 100, 100), True)
    mm.waitForMovementFinished()

    loadMeshpoints()

    calibrateMeshpoints("M", meshMagnet)
    cm.saveMeshpoints("M", meshMagnet)

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
        dr.writeImage(image, "camera.jpg", directory="/var/www/html")
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

        dr.writeImage(markedImage, "marked.jpg", directory="/var/www/html")
        dr.writeImage(transformedImage, "transformed.jpg", directory="/var/www/html")

        print("http://" + cm.clientIdentity["IP"] + "/image.html")
        if needsWarping:
            print("currently warping, use this only if really needed (processing time of ~1 second)")
        else:
            print("currently cropping, switch to warping only if really needed (processing time of ~1 second)")
        print('Image OK? (y/c/w) [yes/crop/warp]')
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
    exit(0)

if args.feedratePercentage != cs.FEEDRATE_PERCENTAGE:
    mm.setFeedratePercentage(args.feedratePercentage)

if args.doHoming:
    mm.doHoming()
    exit(0)

if args.start:
    if (args.infinity):
        i=0
        err=0
        result=-1
        while(True):
            i+=1
            if (err == 3):  # prevents bad runs
                err = 0
                i = 1
                mm.doHoming()
                search_die()

            result_old=result
            found,result=start_script()
            print(result)

            if ((not found) or (result_old==result)):
                err+=1
            else:
                err=0

            if(args.cal_on_run>0):
                if(np.mod(i,args.cal_on_run)==0):
                    mm.doHoming()
                    mm.waitForMovementFinished()
    else:
        start_script()
    exit(0)

pos = Position(args.position[0], args.position[1], args.position[2])
if pos.isValid():
    mm.moveToPos(pos, args.segmented)

