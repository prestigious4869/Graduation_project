import cv2
import numpy as np
# 提取图像特征

img = cv2.imread('test_1.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

sift = cv2.SIFT_create()
kp = sift.detect(gray, None)

img = cv2.drawKeypoints(gray, kp, img)

cv2.imshow('img', img)
cv2.waitKey()
cv2.destroyAllWindows()

kp, des = sift.compute(gray, kp)
print(np.array(kp).shape)
print(des.shape)
print(des[0])