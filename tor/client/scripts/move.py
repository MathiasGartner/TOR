import sys
#sys.path.append("C:\\Users\\David\\Documents\\TOR")

import argparse
import time
import numpy as np
import os

from tor.client import ClientSettings as cs
from tor.client.MovementManager import MovementManager
from tor.client.Position import Position
from tor.base.DieRecognizer import DieRecognizer
from tor.client.Camera import Camera




parser = argparse.ArgumentParser()
parser.add_argument("position", nargs='*', default=[cs.CENTER_TOP.x, cs.CENTER_TOP.y, cs.CENTER_TOP.z], type=float)
parser.add_argument("-f", dest="feedratePercentage", default=cs.FEEDRATE_PERCENTAGE, type=int)
parser.add_argument("-c", dest="doHoming", action="store_true")
parser.add_argument("-s", dest="segmented", action="store_true")
parser.add_argument("-start", dest='start', action="store_true")
parser.add_argument("-find", dest='find', action="store_true")
parser.add_argument("-points", dest='points', action="store_true")
parser.add_argument("-infinity",dest='infinity', action="store_true")
parser.add_argument("-spoints", dest='spoints',action='store_true') #validate starting points
parser.add_argument("-cor", dest="cal_on_run", default=0, type=int)
args = parser.parse_args()

mm = MovementManager()
mm.initBoard()
time.sleep(0.5)

def find_die():
    dr = DieRecognizer()
    cam = Camera()
    mm.setLed(200)
    image = cam.takePicture()
    time.sleep(1)
    mm.setLed(0)
    found, diePosition, result, processedImages = dr.getDiePosition(image, returnOriginalImg=True)
    dr.writeImage(processedImages[0])
    dr.writeRGBArray(processedImages[0])
    print(result)
    found=False #for the moment finding doesn't work
    cam.cam.close()
    if (found):
        print(diePosition)
        mm.moveToPos(Position(120,200,100), True)
        mm.waitForMovementFinished()
        mm.moveToPos(Position(min(diePosition.x , 241), diePosition.y, 50), True)
        mm.waitForMovementFinished()
        mm.moveToPos(Position(min(diePosition.x , 241), diePosition.y, 205), True)
        mm.waitForMovementFinished()
        mm.moveToPos(Position(120,200,100), True)
        mm.waitForMovementFinished()
    else:
        print('Die not found')
        search_die()

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
    if(os.path.isfile('meshpoints.dat')):
        print('Custom configuration found')
        co=np.loadtxt('meshpoints.dat')
        p1 = co[0, :]
        p2 = co[1, :]
        p3 = co[2, :]
        p4 = co[3, :]
        p5 = co[4, :]
        p6 = co[5, :]
        p7 = co[6, :]
        p8 = co[7, :]
        p9 = co[8, :]
        p10 = co[9, :]
        p11 = co[10, :]
        p12 = co[11, :]
    else:
        print('No configuration found')
        p1 = (0, 242, 198)
        p2 = (121,242,200)
        p3 = (242, 242, 203)
        p4 = (0, 150, 201)
        p5 = (121,150.5,204)
        p6 = (242, 150, 203)
        p7=(0,130,140)
        p8 = (121, 130, 140)
        p9=(242,130,140)
        p10=(0, 40, 65)
        p11=(121,40,65)
        p12 = (242, 40, 65)
    n_rows=4 # rows per area
    ramp=False # Does ramp need search?
    mm.moveToPos(Position(p1[0],p1[1], 100))
    mm.moveToPos(Position(p1[0],p1[1], p1[2]))
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
    if (os.path.isfile('startpoints.dat')):
        cos=np.loadtxt('startpoints.dat')
        spos=cos[np.random.randint(0,4),:]
        mm.waitForMovementFinished()
        mm.moveToPos(Position(spos[0], spos[1]+20, 50), True)
        mm.waitForMovementFinished()
        mm.setFeedratePercentage(50)
        mm.moveToPos(Position(spos[0], spos[1]+10, spos[2]+10), True)
        mm.waitForMovementFinished()
        mm.setFeedratePercentage(30)
        mm.moveToPos(Position(spos[0], spos[1], spos[2]), True)
        mm.waitForMovementFinished()
    else:
        mm.waitForMovementFinished()
        mm.moveToPos(Position(140, 30, 50), True)
        mm.waitForMovementFinished()
        mm.setFeedratePercentage(50)
        mm.moveToPos(Position(140, 10, 8), True)
        mm.waitForMovementFinished()
        mm.setFeedratePercentage(30)
        mm.moveToPos(Position(140, 3, 0), True)
        mm.waitForMovementFinished()
    mm.setFeedratePercentage(250)
    time.sleep(2)
    mm.rollDie()
    if (args.find):
        time.sleep(3)
        find_die()

if args.points:
    if(os.path.isfile('meshpoints.dat')):
        print('Load coordinates')
        co=np.loadtxt('meshpoints.dat')
    else:
        #default settings
        co=np.array([[0, 242, 198],
                     [121,242,200],
                     [242, 242, 203],
                     [0, 150, 201],
                     [121,150.5,204],
                     [242, 150, 203],
                     [0,130,140],
                     [121, 130, 140],
                     [242,130,140],
                     [0, 40, 65],
                     [121,40,65],
                     [242, 40, 65]])
    for i in range(12):
        if(i+1==7):
            #overcome ramp
            mm.moveToPos(Position(co[5, 0], co[5, 1], 60), True)
            mm.waitForMovementFinished()
        print('Searching point', i+1)
        searching=True
        while(searching):
            mm.moveToPos(Position(co[i,0], co[i,1], co[i,2]), True)
            mm.waitForMovementFinished()
            print('Position OK? (y/n)')
            if (input()=='y'): searching=False
            else:
                print('Current position')
                print(mm.getCurrentPosition())
                print('New position')
                co[i, 0] = input('x:')
                co[i, 1] = input('y:')
                co[i, 2] = input('z:')
    np.savetxt('meshpoints.dat',co)
    exit(0)

if args.spoints:
    mm.setFeedratePercentage(50)
    mm.moveToPos(Position(120, 100, 100), True)
    mm.waitForMovementFinished()
    if(os.path.isfile('startpoints.dat')):
        print('Load coordinates')
        co=np.loadtxt('startpoints.dat')
    else:
        #default settings
        co=np.array([[60,20,25],
                    [110,20,25],
                    [160,20,25],
                    [220,20,25]])
    for i in range(4):
        mm.setFeedratePercentage(50)
        print('Searching point', i+1)
        searching=True
        while(searching):
            mm.moveToPos(Position(co[i,0], co[i,1]+20, co[i,2]+10), True)
            mm.waitForMovementFinished()
            mm.moveToPos(Position(co[i, 0], co[i, 1] , co[i, 2]), True)
            mm.waitForMovementFinished()
            mm.setFeedratePercentage(30)
            time.sleep(2)
            mm.rollDie()
            print('Position OK? (y/n/c)')
            answ=input()
            if (answ=='y'):
                searching=False
                mm.setFeedratePercentage(100)
                mm.moveToPos(Position(120, 150, 100), True)
                mm.waitForMovementFinished()
                search_die()
                mm.waitForMovementFinished()
            elif (answ=='n'):
                print('Current position')
                print(mm.getCurrentPosition())
                mm.moveToPos(Position(co[i, 0], co[i, 1] + 20, co[i, 2] + 20), True)
                mm.waitForMovementFinished()
                print('New position')
                co[i, 0] = input('x:')
                co[i, 1] = input('y:')
                co[i, 2] = input('z:')
            else:
                mm.doHoming()
                mm.setFeedratePercentage(400)
                mm.moveToPos(Position(120, 100, 50), True)
                mm.waitForMovementFinished()
                mm.setFeedratePercentage(50)
                print('New position')
                co[i, 0] = input('x:')
                co[i, 1] = input('y:')
                co[i, 2] = input('z:')
    np.savetxt('startpoints.dat',co)
    exit(0)

if args.feedratePercentage != cs.FEEDRATE_PERCENTAGE:
    mm.setFeedratePercentage(args.feedratePercentage)

if args.doHoming:
    mm.doHoming()
    exit(0)

#args.start=True



if args.start:
    if (args.infinity):
        i=0
        while(True):
            i+=1
            start_script()
            if(args.cal_on_run>0):
                if(np.mod(i,args.cal_on_run)==0):
                    mm.doHoming()
                    mm.waitForMovementFinished()
    else:
        start_script()
    exit(0)


pos = Position(args.position[0], args.position[1], args.position[2])
if pos.isValid():
    mm.moveToPos(pos,args.segmented)

