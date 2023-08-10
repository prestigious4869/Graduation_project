import json

import cv2
import numpy as np
from matplotlib import pyplot as plt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
import qrcode
import zlib
import lzma


class AesCrypto():
    def __init__(self, key, IV):
        self.key = key.encode("utf-8")
        self.iv = IV.encode("utf-8")
        self.mode = AES.MODE_CBC

    # 加密函数，text参数的bytes类型必须位16的倍数，不够的话，在末尾添加"\0"(函数内以帮你实现)
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.iv)  # self.key的bytes长度是16的倍数即可， self.iv必须是16位
        length = 16
        count = len(text)
        if (count % length != 0):
            add = length - (count % length)
        else:
            add = 0

        text = text + ("\0".encode() * add)  # 这里的"\0"必须编码成bytes，不然无法和text拼接

        self.ciphertext = cryptor.encrypt(text)
        return (self.ciphertext)

    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.iv)
        plain_text = cryptor.decrypt((text)).decode()
        # return plain_text.rstrip("\0")  有的博客上有这句，其实decode解码之后"\0"自动就没有了
        return plain_text


def erode(img):
    # 设置卷积核
    kernel = np.ones((3,3), np.uint8)
    # 图像腐蚀处理
    img = cv2.erode(img, kernel)
    return img


def show_img(title, image):
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def sobelx(img):
    x = cv2.Sobel(img, cv2.CV_16S, 1, 0, ksize=3)
    y = cv2.Sobel(img, cv2.CV_16S, 0, 1, ksize=3)
    absX = cv2.convertScaleAbs(x)
    absY = cv2.convertScaleAbs(y)
    img = cv2.addWeighted(absX, 1, absY, 0, 0)
    return img


def scharr(img):
    x = cv2.Scharr(img, cv2.CV_16S, 1, 0)
    y = cv2.Scharr(img, cv2.CV_16S, 0, 1)
    absX = cv2.convertScaleAbs(x)
    absY = cv2.convertScaleAbs(y)
    img = cv2.addWeighted(absX, 1, absY, 0, 0)
    return img


def sobelxy(img):
    x = cv2.Sobel(img, cv2.CV_16S, 1, 0, ksize=5)
    y = cv2.Sobel(img, cv2.CV_16S, 0, 1, ksize=5)
    absX = cv2.convertScaleAbs(x)
    absY = cv2.convertScaleAbs(y)
    img = cv2.addWeighted(absX, 0.8, absY, 0.2, 0)
    return img


def canny(img):
    # canny边缘检测
    img = cv2.Canny(img, 10, 30, apertureSize=5, L2gradient=True)
    show_img("canny", img)
    return img


def orb(img):
    # ORB特征检测法
    orb = cv2.ORB_create()
    kp, des = orb.detectAndCompute(img, None)
    return img, kp, des


def brisk(img):
    # brisk特征检测法
    brisk = cv2.BRISK_create()
    kp, des = brisk.detectAndCompute(img, None)
    return img, kp, des


def sift(img):
    s = cv2.SIFT_create()
    kp, des = s.detectAndCompute(img, None)
    return img, kp, des


def guass(img):
    # 高斯滤波
    blur = cv2.GaussianBlur(img, (5,5), 0)
    return blur


def clahe(img, x, n):
    # clahe均衡化
    clahe = cv2.createCLAHE(clipLimit=n, tileGridSize=(x,x))
    img = clahe.apply(img)
    return img


def surf(img):
    s = cv2.xfeatures2d.SURF_create()
    kp, des = s.detectAndCompute(img, None)
    return img, kp, des


def show_two_image(img1, img2):
    imgs = np.hstack([img1, img2])
    show_img('1', imgs)


img1 = cv2.imread("../vein001_1/01.jpg", cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread("../vein001_1/03.jpg", cv2.IMREAD_GRAYSCALE)
show_two_image(img1, img2)

#INTER_NEAREST INTER_LINEAR INTER_AREA INTER_CUBIC INTER_LANCZOS4
img1 = cv2.resize(img1, (40,120), interpolation=cv2.INTER_LINEAR)
img2 = cv2.resize(img2, (40,120), interpolation=cv2.INTER_LINEAR)


img1 = clahe(img1,2,2)
img2 = clahe(img2,2,2)
img1 = guass(img1)
img2 = guass(img2)
# img1 = cv2.bilateralFilter(src=img1, d=5, sigmaColor=100, sigmaSpace=100)
# img2 = cv2.bilateralFilter(src=img2, d=5, sigmaColor=100, sigmaSpace=100)

# # 直方图均衡化
# img1 = cv2.equalizeHist(img1)
# show_img("equal", img1)
# img2 = cv2.equalizeHist(img2)
# show_img("equal", img2)
img1 = clahe(img1,2,2)
img2 = clahe(img2,2,2)

img1 = scharr(img1)
img2 = scharr(img2)

# 直方图均衡化
img1 = cv2.equalizeHist(img1)
img2 = cv2.equalizeHist(img2)
img1 = clahe(img1,2,1)
img2 = clahe(img2,2,1)
# img1 = guass(img1)
# img2 = guass(img2)
# img1 = clahe(img1,2,1)
# img2 = clahe(img2,2,1)
# show_img("img1", img1)
# show_img("img2", img2)
show_two_image(img1, img2)

img1, kp1, des1 = sift(img1)
img2, kp2, des2 = sift(img2)

img1_info = []
for kp in kp1:
    info = [kp.angle, kp.octave, kp.pt, kp.response, kp.size]
    img1_info.append(info)


# 加密与解密，并生成二维码
text = str(img1_info).replace(' ', '').replace('[', '').replace(']', '').replace(',', ' ').encode()
pc = AesCrypto(key="keyskeyskeyskeyskeyskeyskeyskeys", IV="keyskeyskeyskeys")
e = pc.encrypt(text)  # 加密数据
e = str(e)


# qrObject = qrcode.QRCode()
# # add data to the QR code
# qrObject.add_data(e)
# # compile the data into a QR code array
# qrObject.make()
# img = qrObject.make_image(fill_color="red")
# with open('test.jpg', 'wb') as f:
#     img.save(f)
#     img = cv2.imread('test.jpg')
#     img = cv2.resize(img, (150,150), interpolation=cv2.INTER_LINEAR)
#     cv2.imwrite('test.jpg', img)

# FLANN
# sift,surf
index_params = dict(algorithm=0, trees=5)
# # # orb
# # index_params = dict(algorithm=6, table_number=6, key_size=12)
search_params = dict(checks=50)
flann = cv2.FlannBasedMatcher(index_params, search_params)
matches = flann.knnMatch(des1, des2, k=2)
# 准备一个空的掩膜来绘制好的匹配
mask_matches = [[0, 0] for i in range(len(matches))]
# 向掩膜中添加数据
matching_points = 0
for i, (m, n) in enumerate(matches):
    if m.distance < 0.7*n.distance:
        mask_matches[i] = [1, 0]
        matching_points += 1
img_matches = cv2.drawMatchesKnn(img1, kp1, img2, kp2, matches, None,
                                 matchColor=(0, 255, 0), singlePointColor=(255, 0, 0),
                                 matchesMask=mask_matches, flags=0)

show_img("knn", img_matches)


# # 暴力匹配
# bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
# matches = bf.match(des1, des2)
# matches = sorted(matches, key=lambda x: x.distance)
# img_matches = cv2.drawMatches(img1, kp1, img2, kp2, matches[:50], img2, flags=2)
# show_img("bf", img_matches)

# ret,img=cv2.threshold(img, 127, 255, cv2.THRESH_BINARY);
# show_img("threshold", img)

# 腐蚀
# img1 = erode(img1)
# img2 = erode(img2)
# 膨胀
# kernel = np.ones((3,3), np.uint8)
# img2 = cv2.dilate(img2, kernel, iterations=1)
# img1 = cv2.dilate(img1, kernel, iterations=1)