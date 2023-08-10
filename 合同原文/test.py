from PIL import Image
import pytesseract
from pytesseract import Output
import cv2
import os
import qrcode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
import pyzbar
import codecs
import zxing
from pyzbar.pyzbar import decode


# def findQrcodeLoc(contract_img):
#     text = pytesseract.image_to_boxes(contract_img, output_type=Output.DICT, lang='chi_sim')
#     pos = {}
#     for i in range(0, len(text['char'])-6):
#         if text['char'][i] == '%' and text['char'][i+1] == "在" and text['char'][i+2] == "此" and text['char'][i+3] == "处" and text['char'][i+4] == "盖" and text['char'][i+5] == "章" :
#             pos["%"] = (text['left'][i], text['top'][i])
#             pos["在"] = (text['left'][i+1], text['top'][i+1])
#             pos["此"] = (text['left'][i+2], text['top'][i+2])
#             pos["处"] = (text['left'][i+3], text['top'][i+3])
#             pos["盖"] = (text['left'][i+4], text['top'][i+4])
#             pos["章"] = (text['left'][i+5], text['top'][i+5])
#     return pos["%"]


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

# 找到粘贴二维码的位置
# img = Image.open("./北京市服务业.jpg")
# text = pytesseract.image_to_boxes(img, output_type=Output.DICT, lang='chi_sim')
# pos = {}
# for i in range(0, len(text['char'])-6):
#     if text['char'][i] == '%' and text['char'][i+1] == "在" and text['char'][i+2] == "此" and text['char'][i+3] == "处" and text['char'][i+4] == "盖" and text['char'][i+5] == "章" :
#         pos["%"] = (text['left'][i], text['top'][i])
#         pos["在"] = (text['left'][i+1], text['top'][i+1])
#         pos["此"] = (text['left'][i+2], text['top'][i+2])
#         pos["处"] = (text['left'][i+3], text['top'][i+3])
#         pos["盖"] = (text['left'][i+4], text['top'][i+4])
#         pos["章"] = (text['left'][i+5], text['top'][i+5])
# print(pos)

# 加密与解密，并生成二维码
text = "want to get info".encode()
pc = AesCrypto(key="keyskeyskeyskeyskeyskeyskeyskeys", IV="keyskeyskeyskeys")
# e = pc.encrypt(text)  # 加密数据
# e = str(e)
#
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

filename = "13892451896finish.jpg"

reader = zxing.BarCodeReader()
barcode = reader.decode(filename)
print(barcode.parsed)

# # read the QRCODE image
# image = cv2.imread(filename)
# cv2.imshow("Output", image)
# cv2.waitKey(0)
# # initialize the cv2 QRCode detector
# detector = cv2.QRCodeDetector()
# # detect and decode
# data, vertices_array, binary_qrcode = detector.detectAndDecode(image)
# # if there is a QR code
# # print the data
# print(data)
# if vertices_array is not None:
#     print("QRCode data:")
#     data = data.split("\'")[1]
#     data = codecs.escape_decode(data)[0]
#     d = pc.decrypt(data)  # 解密数据
#     print(d)
# else:
#     print("There was some error")

# 将二维码贴在合同上
# erweima = Image.open("test.jpg")
# contract = Image.open("北京市服务业.jpg")
# left,top = findQrcodeLoc(contract)
# contract.paste(erweima, (left, contract.size[1]-top))
# contract.save("result.jpg")


# text = pytesseract.image_to_string(Image.open("./北京市服务业.jpg"), lang='chi_sim')
# cv2.imshow("Image", image)
# cv2.imshow("Output", gray)
# cv2.waitKey(0)