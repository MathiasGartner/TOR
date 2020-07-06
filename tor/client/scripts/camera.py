
import argparse

from tor.base.DieRecognizer import DieRecognizer
from tor.client.Camera import Camera

parser = argparse.ArgumentParser()
parser.add_argument("-o", dest="outFilePath", default="image.jpg")
args = parser.parse_args()

cam = Camera()
dr = DieRecognizer()

image = cam.takePicture()

dr.writeImage(image, args.outFilePath)