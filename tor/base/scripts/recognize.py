import cv2
import math
import numpy as np
import matplotlib.pyplot as plt

import tor.TORSettingsLocal as tsl

from tor.base.DieRecognizer import DieRecognizer

def createImageTable(images, cols):
    shape = images[0].shape
    finalImage = np.zeros((shape[0]*cols, shape[1]*math.ceil(len(images)/cols),3),dtype=np.uint8)
    for i in range(len(images)):
        x = (i % cols) * shape[0]
        y = math.floor(i / cols) * shape[1]
        finalImage[x:x+shape[0], y:y+shape[1]] = images[i]
    return finalImage


tags = []

######################################################################################################################
directory = r"C:\\Users\\Michaela\\Documents\\physik\\AEC_Projekt\\michi2\\"
file_extension = ".jpg"
start, end = 1, 1

# path, start, end = directory + r"Elektronik\Raspi\2_0_testen Kamera\bild{}.jpg", 1, 9
# tags = (4, 6, 6, 6, 6, 0, 5, 5, 5) #5/9
# path, start, end = directory + r"Elektronik\Raspi\2_1_glasklar\test{:04d}.jpg", 0, 16
# tags = (2, 0, 1, 5, 4, 6, 0, 1, 5, 1, 2, 2, 3, 0, 2, 3, 3) #17/17
# path, start, end = directory + r"Elektronik\Raspi\2_1_glasklar\bild{}.jpg", 1, 25
# tags = (5, 5, 5, 5, 5, 5, 5, 5, 4, 2, 1, 1, 4, 3, 3, 3, 2, 1, 6, 0, 1, 4, 4, 2, 2) #23/25 (16,19)
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


params_iterator = range(start, end+1)

######################################################################################################################
directory = tsl.DIRECTORY_TEST_IMAGES


# path = directory+r'20200716_unten\iso={}_shutter={}_contrast={}{}'
# file_extension = ".npy"
# iso = [100,200] #100,200,400,800
# shutter = range(20000, 80001, 20000)  #(20000, 100001, 20000)
# contrast = range(0, 81, 40)  #(0, 81, 20)
# params_iterator = [(i, s, c) for i in iso for s in shutter for c in contrast]
# tags = [6]*50


# path = directory+r'20200719 - tests\img ({}){}'
# file_extension = ".npy"
# params_iterator = range(1,81)
# tags = (2,6,5,3,4,1,3,2,4,5,1,3,2,1,6,2,5,4,1,1,1,5,4,4,2,2,1,4,1,0,5,0,0,0,5,3,2,1,5,4,1,3,4,1,5,6,4,3,1,1,5,3,
#         3,2,6,3,5,6,3,1,0,0,4,5,1,4,5,4,0,1,6,5,5,3,6,6,2,2,6,5,1)



# path = directory+r'20200719 - oben\img ({}){}'
# file_extension = ".npy"
# params_iterator = range(1,20)
# tags = (6,6,6,5,2,4,4,6,3,1,2,3,4,4,5,4,0,2,2)
#
# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200719 - fail\\"
# path, start, end = directory + r"img ({}).npy", 1,3
# tags = [4, 4, 1, 6, 1, 4, 5, 3, 4, 2, 3, 3 ,2, 5, 2, 4, 5, 1, 6, 5, 0, 1, 5]
#
#
# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200719 - tests\\"
# path, start, end = directory + r"img ({}).npy", 1, 25
# tags = [4, 4, 1, 6, 1, 4, 5, 3, 4, 2, 3, 3 ,2, 5, 2, 4, 5, 1, 6, 5, 0, 1, 5]
#
#
# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200721 - tests\\"
# path, start, end = directory + r"img ({}).npy", 1, 10
# tags = [4, 4, 1, 6, 1, 4, 5, 3, 4, 2, 3, 3 ,2, 5, 2, 4, 5, 1, 6, 5, 0, 1, 5]
#
# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200723 - mitte\\"
# path, start, end = directory + r"img ({}).npy", 1, 10
# tags = [4, 4, 1, 6, 1, 4, 5, 3, 4, 2, 3, 3 ,2, 5, 2, 4, 5, 1, 6, 5, 0, 1, 5]
#
# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200724 - mitte\\"
# path, start, end = directory + r"img ({}).npy", 1, 1
# tags = [4, 4, 1, 6, 1, 4, 5, 3, 4, 2, 3, 3 ,2, 5, 2, 4, 5, 1, 6, 5, 0, 1, 5]

#path, start, end = directory + r"c{}.jpg", 1, 4
#tags = [4, 4, 4, 4]


# path = tsl.DIRECTORY_TEST_IMAGES + r"20200722 - oben\img ({}){}"
# file_extension = ".npy"
# params_iterator = range(1,122) #1 to 122
# par_list = list(params_iterator)
# tags = np.array([3,1,2,2,5,4,6,1,5,5,4,1,5,3,4,3,4,2,3,5,5,4,6,4,5,6,2,5,3,3,2,6,5,2,2,6,6,4,5,3,5,1,6,6,6,5,2,3,6,5,5,1,1,3,4,
#         5,4,4,5,6,2,6,6,5,1,4,5,5,1,5,0,2,2,1,2,4,4,4,4,3,3,1,1,3,6,4,3,4,6,3,6,4,1,6,2,4,3,1,3,6,6,5,4,4,2,6,1,2,5,1,
#         2,2,5,4,1,2,1,4,5,1,6])[np.array(par_list)-1]
# ###best threshold 100 - 110. score 121/121
#
#
# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200729 - oben - fail\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 10
# tags = [4, 4, 1, 6, 1, 4, 5, 3, 4, 2, 3, 3 ,2, 5, 2, 4, 5, 1, 6, 5, 0, 1, 5]

# path = directory+r'20200722 - oben\20200722 - oben - fail\img ({}){}'
# file_extension = ".npy"
# params_iterator = range(1,29) #1 to 29
# par_list = list(params_iterator)
# tags = np.array([0,3,1,0,0,0,6,0,2,4,0,0,0,0,0,3,2,2,1,0,0,0,0,1,0,0,0,2])[np.array(par_list)-1]
###best threshold 104 or 105. score 28/28

######################################################################################################################

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200826\01\\"
# file_extension = ".jpg"
# path, start, end = directory + r"camera0{}{}", 1, 6
# tags = [5]*6

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200826\04\\"
# file_extension = ".jpg"
# path, start, end = directory + r"camera{}{}", 1, 3
# tags = [2]*3

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200826\07\\"
# file_extension = ".jpg"
# path, start, end = directory + r"camera{}{}", 1, 3
# tags = [6]*3

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200826\10\\"
# file_extension = ".jpg"
# path, start, end = directory + r"camera{}{}", 1, 2
# tags = [1]*2

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200826\13\\"
# file_extension = ".jpg"
# path, start, end = directory + r"camera{}{}", 1, 3
# tags = [3]*3

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200826\16\\"
# file_extension = ".jpg"
# path, start, end = directory + r"camera{}{}", 1, 4
# tags = [1]*4

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200826\19\\"
# file_extension = ".jpg"
# path, start, end = directory + r"camera{}{}", 1, 2
# tags = [2]*2

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200826\22\\"
# file_extension = ".jpg"
# path, start, end = directory + r"camera{}{}", 1, 2
# tags = [2]*2

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200826\25\\"
# file_extension = ".jpg"
# path, start, end = directory + r"camera{:02d}{}", 1, 18
# tags = [2]*18

######################################################################################################################

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\1\found\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 14
# tags = [5,6,3,4,5,1,2,2,5,6,6,3,3,3]  #th [100, 105, 110, 115] [14, 13, 12, 10]
# # end, tags =1, [0]*1

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\2\found\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 13
# tags = [1,1,4,3,3,3,3,1,4,5,5,4,1]  #th [100, 105, 110, 115] [13, 13, 13, 13]

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\3\found\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 3
# tags = [6,4,3]  #th [100, 105, 110, 115] [3, 3, 3, 3]
# end, tags =6, [0]*6

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\4\found\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 12
# tags = [2,2,2,2,0,0,0,0,0,5,5,5]  #th [100, 105, 110, 115] [12, 12, 12, 10]

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\5\found\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 2
# tags = [3, 1]  #th [100, 105, 110, 115] [2, 2, 2, 2]
# # end, tags =6, [0]*6

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\6\found\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 10
# tags = [2]*10  #th [100, 105, 110, 115] [10, 10, 10, 10]

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\7\found\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 12
# tags = [6,0,0,6,2,0,3,0,0,5,5,0]  #th [100, 105, 110, 115] [12, 12, 12, 12], additinalfake blob at 100 in img1
# # end, tags =2, [0]*2

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\8\fail\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 4
# tags = [3,1,2,2]  #th [100, 105, 110, 115] [4, 4, 4, 4]
# end, tags =6, [0]*6 #th [100, 105, 110, 115] [5, 6, 6, 6]

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\9\fail\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 7
# tags = [4,1,5,3,3,3,3]  #th [100, 105, 110, 115] [7, 7, 7, 6]
# end, tags =5, [6,0,0,0,0] #th [100, 105, 110, 115] [4, 4, 4, 4]

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\10\found\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 11
# tags = [1,6,6,6,6,6,6,6,3,3,3]  #th [100, 105, 110, 115] [11, 11, 11, 10]

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\11\found\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 11
# tags = [5,5,5,5,3,6,2,5,5,5,5]  #th [100, 105, 110, 115] [11, 11, 11, 11] additinalfake blob at 100 in img7

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\12\found\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 11
# tags = [6,6,6,6,3,4,1,1,1,1,3]  #th [100, 105, 110, 115] [11, 11, 11, 11]

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\13\found\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 11
# tags = [3,3,3,3,0,6,6,6,6,6,6]  #th [100, 105, 110, 115] [11, 11, 11, 11]
#
# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\14\found\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 16
# tags = [3,5,6,2,3,5,5,1,6,3,3,6,4,4,4,4]  #th [100, 105, 110, 115] [16, 16, 16, 16]

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\15\fail\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 5
# tags = [4,4,4,4,6]  #th [100, 105, 110, 115] [5, 5, 5, 5]
# end, tags =5, [0,0,0,0,0]
#
# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\16\fail\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 4
# tags = [1,1,1,1]  #th [100, 105, 110, 115] [4, 4, 4, 4]
# end, tags =5, [0,0,0,0,0] # [100, 105, 110, 115] [5, 5, 5, 4] additinalfake blob at 115 in img2

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\17\fail\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 9
# tags = [3,6,2,4,4,3,3,3,3]  #th [100, 105, 110, 115] [9, 9, 9, 9]
# end, tags =3, [0]*3

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\18\fail\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 10
# tags = [3,3,3,3,3,5,1,1,6,5]  #th [100, 105, 110, 115] [10, 10, 10, 10]
# end, tags =2, [0]*2

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\19\found\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 9
# tags = [2,2,2,2,1,1,1,1,3]  #th [100, 105, 110, 115] [9, 9, 9, 5]
# # end, tags =1, [0]

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\20\found\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 10
# tags = [3,3,3,3,3,3,3,3,3,3]  #th [100, 105, 110, 115] [10, 10, 10, 10]

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\23\found\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 11
# tags = [4,4,4,4,6,2,1,5,5,5,5]  #th [100, 105, 110, 115] [11, 11, 11, 11]

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\24\found\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 10
# tags = [1,1,1,1,1,1,1,1,1,1]  #th [100, 105, 110, 115] [10, 10, 10, 10]

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\25\fail\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 8
# tags = [5,3,1,1,4,4,4,4]  #th [100, 105, 110, 115] [8, 7, 3, 2]
# end, tags =4, [2,2,1,4] #[100, 105, 110, 115] [3, 2, 0, 0]

# directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\26\fail\\"
# file_extension = ".npy"
# path, start, end = directory + r"img ({}){}", 1, 10
# tags = [6,6,6,6,3,4,3,3,3,3]  #th [100, 105, 110, 115] [10, 10, 10, 10]
# end, tags =1, [1] #[100, 105, 110, 115] [1, 1, 0, 0]

directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200829\27\fail\\"
file_extension = ".jpg"
path, start, end = directory + r"img ({}){}", 1, 6
tags = [3,3,3,3,2,6]  #th [100, 105, 110, 115] [6, 6, 6, 6]
end, tags =3, [0,0,0]

######################################################################################################################

directory = tsl.DIRECTORY_TEST_IMAGES + r"\20200904\essigbaum\found\\"
file_extension = ".jpg"
path, start, end = directory + r"img ({}){}", 1, 9
#tags = [3,3,3,3,2,6]  #th [100, 105, 110, 115] [6, 6, 6, 6]
end, tags = 8, [0, 2, 1, 2, 2, 1, 1, 1]

######################################################################################################################


params_iterator = range(start, end+1)

borderSize = 10
borderCol = (0, 0, 0)
dr = DieRecognizer()

nr_correct_array = []
#thresholds = [100,105,110,115]  #range(40,201,20)
thresholds = [108]

for threshold in thresholds:
    images = []
    results = []
    correct = 0
    j = 0

    for params in params_iterator:
        try:
            len(params)
        except:
            params = (params,)
        im = dr.readDummyImageGeneralized(path, file_extension, *params)
        dieRollResult, resultImg = dr.getDieRollResult(
            im, withUI=False, returnOriginalImg=True, alreadyCropped=True, alreadyGray=False,
            threshold=threshold, markDie=True)
        if len(tags) > j:
            if dieRollResult.result == tags[j]:
                # print("correct ({})".format(dieRollResult.result))
                borderCol = (20, 20, 0)
                correct += 1
            else:
                print("expected {}, found {} in image {}".format(tags[j], dieRollResult.result, path.format(*params, file_extension)))
                borderCol = (0, 0, 255)
        im_border = cv2.copyMakeBorder(resultImg[1], borderSize, borderSize, borderSize, borderSize, cv2.BORDER_CONSTANT, value=borderCol)
        images.append(im_border)
        results.append((dieRollResult.result, path.format(*params, file_extension)))
        j += 1

    nr_correct_array.append(correct)


    print("recognized {}/{} ({}%)".format(correct, len(images), correct/len(images)*100))
    maxImages = 20
    if len(images) > maxImages:
        print("only show first", maxImages, "images")
    allImages = createImageTable(images[:min(maxImages, len(images))], math.ceil(math.sqrt(len(images))))
    cv2.namedWindow("all", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("all", 1600, 1000)
    print([result[0] for result in results])
    cv2.imshow("all", allImages)
    cv2.waitKey()

print(thresholds, nr_correct_array)
plt.plot(list(thresholds), nr_correct_array)
plt.xlabel('threshold')
plt.ylabel('number correct')
plt.title('contrast=80, total {} images'.format(len(images)))
plt.show()
