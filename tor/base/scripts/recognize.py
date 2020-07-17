import cv2
import math
import numpy as np

from tor.base.DieRecognizer import DieRecognizer

def createImageTable(images, cols):
    shape = images[0].shape
    finalImage = np.zeros((shape[0]*cols, shape[1]*math.ceil(len(images)/cols), 3),dtype=np.uint8)
    for i in range(len(images)):
        x = (i % cols) * shape[0]
        y = math.floor(i / cols) * shape[1]
        finalImage[x:x+shape[0], y:y+shape[1]] = images[i]
    return finalImage

tags = []
directory = r"D:\Dropbox\Uni\AEC\\"
#path, start, end = directory + r"Elektronik\Raspi\2_0_testen Kamera\bild{}.jpg", 1, 9
#tags = (4, 6, 6, 6, 6, 0, 5, 5, 5) #5/9
#path, start, end = directory + "Elektronik\Raspi\2_1_glasklar\test{:04d}.jpg", 0, 16
#tags = (2, 0, 1, 5, 4, 6, 0, 1, 5, 1, 2, 2, 3, 0, 2, 3, 3) #17/17
#path, start, end = directory + r"Elektronik\Raspi\2_1_glasklar\bild{}.jpg", 1, 25
#tags = (5, 5, 5, 5, 5, 5, 5, 5, 4, 2, 1, 1, 4, 3, 3, 3, 2, 1, 6, 0, 1, 4, 4, 2, 2) #23/25
#path, start, end = directory + r"Elektronik\Raspi\2_1_glasklar\bild{}.jpg", 26, 50
#tags = (2, 1, 1, 1, 1, 1, 1, 6, 1, 1, 3, 3, 3, 6, 2, 4, 3, 1, 3, 4, 5, 5, 1, 1, 1) #8/25
#path, start, end = directory + r"Elektronik\Raspi\2_1_glasklar\bild{}.jpg", 51, 69
#tags = (1, 1, 1, 1, 1, 5, 4, 2, 3, 2, 6, 2, 5, 5, 5, 5, 4, 4, 1) #12/19
#path, start, end = directory + r"Elektronik\Raspi\2_1_glasklar\bild{}.png", 70, 71
#tags = (1, 1) #2/2
#path, start, end = directory + r"Elektronik\Raspi\2_1_glasklar\bild{}.jpg", 72, 73
#tags = (3, 1) #2/2
#path, start, end = directory + r"Elektronik\Raspi\2_2_neue Kamera testen\image{:03d}.jpg", 0, 13
#tags = (1, 1, 5, 0, 3, 6, 4, 1, 5, 5, 5, 0, 5, 4) #11/14
#path, start, end = directory + r"Elektronik\Raspi\2_2_neue Kamera testen\test{}.jpg", 1, 4
#tags = (5, 6, 2, 0) #4/4

#path, start, end = directory + r"Elektronik\Raspi\2_2_neue Kamera testen\image{:03d}.jpg", 8, 8
#path, start, end = directory + r"Elektronik\Raspi\2_1_glasklar\bild{}.jpg", 15, 15
#path, start, end = directory + r"Elektronik\Raspi\2_1_glasklar\bild{}.jpg", 39, 39 #here the threshold has to be around 85 to 90 because the image is very bright


#path, start, end = directory + r"Elektronik\Raspi\2_3_punkte\1\image{:03d}.jpg", 0, 16
#tags = (5, 1, 3, 6, 4, 5, 3, 6, 5, 4, 1, 1, 3, 5, 0, 0, 0)

#path, start, end = directory + r"Elektronik\Raspi\2_3_punkte\2\image{:03d}.jpg", 0, 24
#tags = (5, 0, 5, 4, 6, 5, 2, 4, 0, 2, 0, 1, 0 ,0, 4, 0, 0, 0, 3, 0, 0, 0, 0, 3, 5)
#path, start, end = directory + r"Elektronik\Raspi\2_3_punkte\2\image{:03d}.jpg", 25, 46
#tags = (5, 0, 0, 0, 0, 4, 0, 2, 0, 2, 6, 0, 1, 4, 0, 0, 0, 0, 3, 1, 4, 6)


directory = r"D:\AEC\DiceImages\20200717\\"
path, start, end = directory + r"img ({}).jpg", 59, 67
tags = [(2, 1, 6, 2, 3, 3, 4, 3, 2, 4, 3, 1, 2, 2, 4, 5, 0, 6, 3, 4)]

#path, start, end = directory + r"Elektronik\Raspi\2_4_leds\testled{:03d}.jpg", 1, 1
#tags = [(3)]

borderSize = 10
borderCol = (0, 0, 0)
dr = DieRecognizer()
images = []
results = []
correct = 0
i = 0
for imNr in range(start, end+1):
    im = dr.readDummyImage(imNr, path)
    #im = dr.readDummyRGBArray(imNr, path)
    found, posMM, result, resultImg = dr.getDiePosition(im, withUI=False, returnOriginalImg=True, alreadyCropped=True)
    if len(tags) > i:
        if result == tags[i]:
            print("correct ({})".format(result))
            borderCol = (20, 20, 0)
            correct += 1
        else:
            print("expected {}, found {} in image {}".format(tags[i], result, path.format(imNr)))
            borderCol = (0, 0, 255)
    im_border = cv2.copyMakeBorder(resultImg[1], borderSize, borderSize, borderSize, borderSize, cv2.BORDER_CONSTANT, value=borderCol)
    images.append(im_border)
    results.append((result, path.format(imNr)))
    i += 1

print("recognized {}/{} ({}%)".format(correct, len(images), correct/len(images)*100))
allImages = createImageTable(images, math.ceil(math.sqrt(len(images))))
cv2.namedWindow("all", cv2.WINDOW_NORMAL)
cv2.resizeWindow("all", 1600, 1000)
cv2.imshow("all", allImages)
cv2.waitKey()
