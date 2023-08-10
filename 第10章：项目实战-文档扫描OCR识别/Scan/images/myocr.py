from PIL import Image
import pytesseract
import cv2
import os


def show_img(image):
    cv2.imshow("image", image)
    cv2.waitKey()
    cv2.destroyAllWindows()


# pre_process = 'blur'
#
# image = cv2.imread('receipt_scan.jpg', 0)
#
# if pre_process == "thresh":
#     image = cv2.threshold(image, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
#
# if pre_process == "blur":
#     image = cv2.medianBlur(image, 3)

text = pytesseract.image_to_string(Image.open("receipt_scan_blur.jpg"))
print(text)
# show_img(image)