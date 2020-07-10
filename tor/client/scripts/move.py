import sys
#sys.path.append("C:\\Users\\David\\Documents\\TOR")

import argparse
import time
import numpy as np

from tor.client import ClientSettings as cs
from tor.client.MovementManager import MovementManager
from tor.client.Position import Position




parser = argparse.ArgumentParser()
parser.add_argument("position", nargs='*', default=[cs.CENTER_TOP.x, cs.CENTER_TOP.y, cs.CENTER_TOP.z], type=float)
parser.add_argument("-f", dest="feedratePercentage", default=cs.FEEDRATE_PERCENTAGE, type=int)
parser.add_argument("-c", dest="doHoming", action="store_true")
parser.add_argument("-ce", dest="doHomingexact", action="store_true")
parser.add_argument("-s", dest="segmented", action="store_true")
parser.add_argument("-start", dest='start', action="store_true")
parser.add_argument("-find", dest='find', action="store_true")
args = parser.parse_args()

mm = MovementManager()
mm.initBoard()
time.sleep(0.5)

def find_die():
    from tor.base.DieRecognizer import DieRecognizer
    from tor.client.Camera import Camera
    dr = DieRecognizer()
    cam = Camera()
    mm.setLed(200)
    image = cam.takePicture()
    time.sleep(1)
    mm.setLed(0)
    found, diePosition, result, processedImages = dr.getDiePosition(image, returnOriginalImg=True)
    # dr.writeImage(processedImages[1])
    print(result)
    if (found):
        print(diePosition)
        mm.moveToPos(Position(min(diePosition.x * 1.1, 241), diePosition.y, 50), args.segmented)
        mm.waitForMovementFinished()
        mm.moveToPos(Position(min(diePosition.x * 1.1, 241), diePosition.y, 205), args.segmented)
    else:
        print('Die not found')
        search_die()

def search_die():
    #starting position
    '''
    p4 p5 p3
    p1 p6 p2
    M      M
    '''
    p1 = (0, 150, 201)
    p2 = (242, 150, 203)
    p3 = (242, 242, 203)
    p4 = (0, 242, 198)
    p5 = (121,242,200)
    p6 = (121,150.5,204)
    n_rows=4
    mm.moveToPos(Position(p4[0],p4[1], 100))
    mm.moveToPos(Position(p4[0],p4[1], p4[2]))
    #raster bottom
    # mesh left side
    x_mesh_l=np.linspace(p4[0],p1[0],n_rows)
    y_mesh_l=np.linspace(p4[1],p1[1],n_rows)
    z_mesh_l=np.linspace(p4[2],p1[2],n_rows)
    #mesh center
    x_mesh_c = np.linspace(p5[0], p6[0], n_rows)
    y_mesh_c = np.linspace(p5[1], p6[1], n_rows)
    z_mesh_c = np.linspace(p5[2], p6[2], n_rows)
    #mesh right side
    x_mesh_r=np.linspace(p3[0], p2[0], n_rows)
    y_mesh_r = np.linspace(p3[1], p2[1], n_rows)
    z_mesh_r = np.linspace(p3[2], p2[2], n_rows)
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
    cur_po = mm.getCurrentPosition()
    mm.moveToPos(Position(cur_po.x, cur_po.y, 100), True)
    mm.waitForMovementFinished()
    '''
    p10 p11 p9
    p7 p12 p8
    M      M
    '''
    p10=(0,130,140)
    p9=(242,130,140)
    p8=(242, 40, 65)
    p7=(0, 40, 65)
    p11=(121,130,140)
    p12=(121,40,65)
    # mesh left side
    x_mesh_l=np.linspace(p10[0],p7[0],n_rows)
    y_mesh_l=np.linspace(p10[1],p7[1],n_rows)
    z_mesh_l=np.linspace(p10[2],p7[2],n_rows)
    #mesh center
    x_mesh_c = np.linspace(p11[0], p12[0], n_rows)
    y_mesh_c = np.linspace(p11[1], p12[1], n_rows)
    z_mesh_c = np.linspace(p11[2], p12[2], n_rows)
    #mesh right side
    x_mesh_r=np.linspace(p9[0], p8[0], n_rows)
    y_mesh_r = np.linspace(p9[1], p8[1], n_rows)
    z_mesh_r = np.linspace(p9[2], p8[2], n_rows)
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
    mm.moveToPos(Position(100,200,100))















if args.feedratePercentage != cs.FEEDRATE_PERCENTAGE:
    mm.setFeedratePercentage(args.feedratePercentage)

if args.doHoming:
    mm.doHoming()
    exit(0)

#args.start=True

if args.doHomingexact:
    mm.moveToPos(Position(120,120,120), args.segmented)
    mm.doHoming()
    mm.waitForMovementFinished()
    mm.moveToPos(Position(120, 120, 100), args.segmented)
    mm.waitForMovementFinished()
    mm.doHoming()
    mm.moveToPos(Position(120, 120, 100), args.segmented)
    exit(0)



if args.start:
    cur_po=mm.getCurrentPosition()
    print(cur_po)
    #mm.moveToPos(Position(cur_po.x, cur_po.y, 50), args.segmented)
    mm.waitForMovementFinished()
    mm.moveToPos(Position(125,50,30), args.segmented)
    mm.waitForMovementFinished()
    mm.setFeedratePercentage(50)
    mm.moveToPos(Position(125, 15, -12), args.segmented)
    mm.waitForMovementFinished()
    mm.moveToPos(Position(130, 6, -15), args.segmented)
    mm.waitForMovementFinished()
    mm.setFeedratePercentage(250)
    time.sleep(2)
    mm.rollDie()
    if (args.find):
        time.sleep(3)
        find_die()
    exit(0)


pos = Position(args.position[0], args.position[1], args.position[2])
if pos.isValid():
    mm.moveToPos(pos,args.segmented)

