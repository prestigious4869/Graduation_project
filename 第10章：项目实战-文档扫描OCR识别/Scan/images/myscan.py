import cv2
import numpy as np


# 同比例缩小或放大
def resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]
    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
    resized = cv2.resize(image, dim, interpolation=inter)
    return resized


# 展示图片
def show_img(image):
    cv2.imshow("image", image)
    cv2.waitKey()
    cv2.destroyAllWindows()


# 将四个点按照左上，右上，右下，左下排列
def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    # 对二维数组中每一行相加，x+y最大的为右下点，最小的为左上点
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    # 对二维数组中每一行进行相减，较小的为右上点，较大的为左下点
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


# 原始图像中轮廓四个顶点的坐标位置为pts
def four_point_transform(image, pts):
    # 确定轮廓四个顶点分别为哪一个位置（左上，右上，左下，右下）
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # 计算输入的w和h值，分别取长宽的最大值最为最终的长宽
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # 变换后对应四个顶点的坐标位置
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # rect：四个顶点原始坐标；dst：四个顶点最终坐标
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped


# 读入图片
image = cv2.imread("receipt.jpg")
orig = image.copy()

image = resize(orig, height=500)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# 高斯模糊，用于边缘检测，更容易画出轮廓
gray = cv2.GaussianBlur(gray, (5, 5), 0)
# 边缘检测，返回一张图像
edged = cv2.Canny(gray, 75, 200)
# 轮廓检测
cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1]
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
# 遍历轮廓
for c in cnts:
    # 计算轮廓近似
    peri = cv2.arcLength(c, True)
    # C表示输入的点集
    # epsilon表示从原始轮廓到近似轮廓的最大距离，它是一个准确度参数
    # True表示封闭的
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    if len(approx) == 4:
        screenCnt = approx
        break
# 在image中绘制出轮廓
cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)

# 透视变换
ratio = orig.shape[0] / 500.0
warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)

# 灰度图
warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
# 二值处理
ref = cv2.threshold(warped, 100, 255, cv2.THRESH_BINARY)[1]
show_img(resize(ref, height=650))

cv2.imwrite("receipt_scan.jpg", ref)
