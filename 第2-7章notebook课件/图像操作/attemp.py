import cv2
import numpy as np
import matplotlib.pyplot as plt


def cv_show(name, img):
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


img = cv2.imread('cat.jpg')
cv_show('image', img)
