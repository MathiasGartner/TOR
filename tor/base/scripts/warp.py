import cv2
import numpy as np

imgPath = r"D:\AEC\DiceImages\20200725 - camera\current_view.jpg"

image = cv2.imread(imgPath)

tl = [30, 70]
tr = [50, 1900]
bl = [1300, 0]
br = [1000, 1500]

h = max((bl[0] - tl[0]), (br[0] - tr[0]))
w = max((tr[1] - tl[1]), (br[1] - bl[1]))

print("w:", w, "h:", h)

src = np.array([tl, bl, tr, br], dtype="float32")

dst = np.array([[0, 0],
                [w-1, 0],
                [0, h-1],
                [w-1, h-1]], dtype="float32")

mat = cv2.getPerspectiveTransform(src, dst)
warped = cv2.warpPerspective(image, mat, (w, h))

cv2.namedWindow("original", cv2.WINDOW_NORMAL)
cv2.resizeWindow("original", 1600, 1000)
cv2.imshow("original", image)

cv2.namedWindow("warp", cv2.WINDOW_NORMAL)
cv2.resizeWindow("warp", w, h)
cv2.imshow("warp", warped)

cv2.waitKey()