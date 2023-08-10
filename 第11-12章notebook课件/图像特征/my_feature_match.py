import cv2
import numpy as np
import matplotlib.pyplot as plt


def show_img(img):
    cv2.imshow('image', img)
    cv2.waitKey()
    cv2.destroyAllWindows()


def BF_match():
    sift = cv2.SIFT_create()
    # 计算特征点与特征向量
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)
    # crossCheck表示两个特征点要互相匹配
    # NPOM_L2：归一化数组的欧几里得距离
    # 一对一匹配
    # bf = cv2.BFMatcher(crossCheck=True)
    # matches = bf.match(des1, des2)
    # matches = sorted(matches, key=lambda x: x.distance)
    # # 取距离最小的前十个点展示
    # img3 = cv2.drawMatches(img1, kp1, img2, kp2, matches[:10], None, flags=2)
    # show_img(img3)

    # k对最佳匹配
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append([m])
    img3 = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good, None, flags=2)
    show_img(img3)

    # cv2.FlannBasedMatcher比cv2.BFMatcher更快


def ransac():


img1 = cv2.imread('box.png', 0)
img2 = cv2.imread('box_in_scene.png', 0)
BF_match()