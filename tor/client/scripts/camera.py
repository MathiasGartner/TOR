
import argparse
import time

from tor.base.DieRecognizer import DieRecognizer
from tor.client.Camera import Camera

parser = argparse.ArgumentParser()
parser.add_argument("-o", dest="outFilePath", default="image.jpg")
parser.add_argument("-t", dest="useTimestamp", action="store_true")
parser.add_argument("-c", dest="cropImage", action="store_true")
parser.add_argument("-d", dest="directory", default="")
args = parser.parse_args()

cam = Camera()
time.sleep(2)
dr = DieRecognizer()

image = cam.takePicture()

print("picture taken")

if args.cropImage:
    image = dr.cropToSearchableArea(image)

if args.useTimestamp:
    dr.writeImage(image, directory=args.directory)
    dr.writeRGBArray(image, directory=args.directory)
else:
    dr.writeImage(image, args.outFilePath, directory=args.directory)
    dr.writeRGBArray(image, args.outFilePath, directory=args.directory)