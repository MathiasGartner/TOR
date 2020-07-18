import cv2
import math
import numpy as np

from tor.base.DieRecognizer import DieRecognizer

# mode = 0 #"iterate over image number"
mode = 1 #"iterate over filenames"

def createImageTable(images, cols):
    shape = images[0].shape
    finalImage = np.zeros((shape[0]*cols, shape[1]*math.ceil(len(images)/cols), 3),dtype=np.uint8)
    for i in range(len(images)):
        x = (i % cols) * shape[0]
        y = math.floor(i / cols) * shape[1]
        finalImage[x:x+shape[0], y:y+shape[1]] = images[i]
    return finalImage

tags = []
directory = r"C:\\Users\\Michaela\\Documents\\physik\\AEC_Projekt\\michi2\\"

# path, start, end = directory + r"Elektronik\Raspi\2_0_testen Kamera\bild{}.jpg", 1, 9
# tags = (4, 6, 6, 6, 6, 0, 5, 5, 5) #5/9
# path, start, end = directory + r"Elektronik\Raspi\2_1_glasklar\test{:04d}.jpg", 0, 16
# tags = (2, 0, 1, 5, 4, 6, 0, 1, 5, 1, 2, 2, 3, 0, 2, 3, 3) #17/17
path, start, end = directory + r"Elektronik\Raspi\2_1_glasklar\bild{}.jpg", 1, 25
tags = (5, 5, 5, 5, 5, 5, 5, 5, 4, 2, 1, 1, 4, 3, 3, 3, 2, 1, 6, 0, 1, 4, 4, 2, 2) #23/25 (16,19)
# path, start, end = directory + r"Elektronik\Raspi\2_1_glasklar\bild{}.jpg", 26, 50
# tags = (2, 1, 1, 1, 1, 1, 1, 6, 1, 1, 3, 3, 3, 6, 2, 4, 3, 1, 3, 4, 5, 5, 1, 1, 1) #8/25
# path, start, end = directory + r"Elektronik\Raspi\2_1_glasklar\bild{}.jpg", 51, 69
# tags = (1, 1, 1, 1, 1, 5, 4, 2, 3, 2, 6, 2, 5, 5, 5, 5, 4, 4, 1) #12/19
# path, start, end = directory + r"Elektronik\Raspi\2_1_glasklar\bild{}.png", 70, 71
# tags = (1, 1) #2/2
# path, start, end = directory + r"Elektronik\Raspi\2_1_glasklar\bild{}.jpg", 72, 74
# tags = (3, 1, 1) #3/3

# path, start, end = directory + r"Elektronik\Raspi\2_2_neue Kamera testen\image{:03d}.jpg", 0, 13
# tags = (1, 1, 5, 0, 3, 6, 4, 1, 5, 5, 5, 0, 5, 4) #11/14
# path, start, end = directory + r"Elektronik\Raspi\2_2_neue Kamera testen\test{}.jpg", 1, 4
# tags = (5, 6, 2, 0) #4/4

#path, start, end = directory + r"Elektronik\Raspi\2_2_neue Kamera testen\image{:03d}.jpg", 8, 8
#path, start, end = directory + r"Elektronik\Raspi\2_1_glasklar\bild{}.jpg", 15, 15
#path, start, end = directory + r"Elektronik\Raspi\2_1_glasklar\bild{}.jpg", 39, 39 #here the threshold has to be around 85 to 90 because the image is very bright


# path, start, end = directory + r"Elektronik\Raspi\2_3_punkte\1\image{:03d}.jpg", 0, 16
# tags = (5, 1, 3, 6, 4, 5, 3, 6, 5, 4, 1, 1, 3, 5, 0, 0, 0) #17/17
# path, start, end = directory + r"Elektronik\Raspi\2_3_punkte\2\image{:03d}.jpg", 0, 24
# tags = (5, 0, 5, 4, 6, 5, 2, 4, 0, 2, 0, 1, 0 ,0, 4, 0, 0, 0, 3, 0, 0, 0, 0, 3, 5)  #23/25
# path, start, end = directory + r"Elektronik\Raspi\2_3_punkte\2\image{:03d}.jpg", 25, 46
# tags = (5, 0, 0, 0, 0, 4, 0, 2, 0, 2, 6, 0, 1, 4, 0, 0, 0, 0, 3, 1, 4, 6)

#
# path, start, end = directory + r"Elektronik\Raspi\2_4_leds\testled{:03d}.jpg", 1, 1
# tags = [(3)]

######################################################################################################################
directory = r"C:\\Users\\Michaela\\Documents\\physik\\AEC_Projekt\\testimages\\"

# path, start, end = directory + r"topled\test{:03d}.jpg", 1, 18
# tags = (4,4,4,4,4,6,6,2,2,2,5,5,2,2,2,2,3,3) #,3,3,2,6,6,3)
# path, start, end = directory + r"blue_0_0_100\test{:03d}.jpg", 1, 12
# tags = (2,2,3,5,5,1,2,3,3,3,1,4)
# path, start, end = directory + r"green_0_100_0\test{:03d}.jpg", 1, 14
# tags = (1,4,4,1,1,1,3,6,4,5,5,5,3,2)
# path, start, end = directory + r"red_100_0_0\test{:03d}.jpg", 1, 12
# tags = (2,2,3,5,4,4,2,1,4,6,3,1)
# path, start, end = directory + r"bunt\test{:03d}.jpg", 1, 21
# tags = (4,6,2,1,1,5,1,1,5,6,4,2,6,6,5,6,2,2,4,6,4)
# path, start, end = directory + r"iso_100\test{:03d}.jpg", 1, 17
# tags = (1,3,6,5,1,1,4,1,3,2,2,6,5,5,4,1,3)
# path, start, end = directory + r"iso_300\test{:03d}.jpg", 1, 14
# tags = (3,6,2,1,5,6,2,5,5,1,5,5,1,2)
# path, start, end = directory + r"wuerfel_unter_cube\test{:03d}.jpg", 1, 20
# tags = (1,1,1,1,1,1,1,1,1,1,3,3,3,3,3,3,3,3,3,3)
# path, start, end = directory + r"wuerfel_unter_cube\test{:03d}.jpg", 21, 40
# tags = (6,6,6,6,6,6,6,6,6,6,5,5,5,5,5,5,5,5,5,5)

######################################################################################################################
directory = r"C:\\Users\\Michaela\\Documents\\physik\\AEC_Projekt\\testimages\\"


iso = [100, 200] #100,200,400,800
shutter = range(20000, 50001, 20000)
contrast = range(0, 81, 20)

filename_raw = directory+r'20200716_unten\iso={}_shutter={}_contrast={}.{}'
path=filename_raw
tags = [6]*40




borderSize = 10
borderCol = (0, 0, 0)
dr = DieRecognizer()
images = []
results = []
correct = 0
j = 0

if mode == 0:
    for imNr in range(start, end+1):
        im = dr.readDummyImage(imNr, path)
        found, posMM, result, resultImg = dr.getDiePosition(im, withUI=False, returnOriginalImg=False)
        if len(tags) > j:
            if result == tags[j]:
                print("correct ({})".format(result))
                borderCol = (20, 20, 0)
                correct += 1
            else:
                print("expected {}, found {} in image {}".format(tags[j], result, path.format(imNr)))
                borderCol = (0, 0, 255)
        im_border = cv2.copyMakeBorder(resultImg[1], borderSize, borderSize, borderSize, borderSize, cv2.BORDER_CONSTANT, value=borderCol)
        images.append(im_border)
        results.append((result, path.format(imNr)))
        j += 1
elif mode == 1:

    for i, s, c in [(i, s, c) for i in iso for s in shutter for c in contrast]:
        filename = filename_raw.format(i, s, c, "{}")
        im = np.load(filename.format("npy"))
        # im = dr.readDummyImage(imNr, path)
        found, posMM, result, resultImg = dr.getDiePosition(im, withUI=False, returnOriginalImg=False)
        if len(tags) > j:
            if result == tags[j]:
                print("correct ({})".format(result))
                borderCol = (20, 20, 0)
                correct += 1
            else:
                print("expected {}, found {} in image {}".format(tags[j], result, path.format(i,s,c,"npy")))
                borderCol = (0, 0, 255)
        im_border = cv2.copyMakeBorder(resultImg[1], borderSize, borderSize, borderSize, borderSize, cv2.BORDER_CONSTANT, value=borderCol)
        images.append(im_border)
        results.append((result, path.format(i, s, c, "npy")))
        j += 1

else:
    print("no valid mode specified. specify mode=0 or mode=1 at the beginning of the file")


print("recognized {}/{} ({}%)".format(correct, len(images), correct/len(images)*100))
allImages = createImageTable(images, math.ceil(math.sqrt(len(images))))
cv2.namedWindow("all", cv2.WINDOW_NORMAL)
cv2.resizeWindow("all", 1600, 1000)
print([result[0] for result in results])
cv2.imshow("all", allImages)
cv2.waitKey()
