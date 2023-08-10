import calendar
import hashlib
import json
import os
import time
import shutil
import pathlib
import base64
import numpy as np
from matplotlib import pyplot as plt
import cv2
import pymysql
from PIL import Image
import pytesseract
import qrcode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
import pyzbar
import codecs
from pytesseract import Output
from flask import Flask, session, render_template, request, send_file
from flask_cors import CORS
import zxing

app = Flask(__name__)
app.config["SECRET_KEY"] = "dtj"
CORS(app, resources=r'/*')


@app.route('/', methods=['GET'])
def init():
    return render_template('public/login.html')


@app.route('/exit', methods=['POST'])
def exit():
    session.pop('user_id')
    return "success"


@app.route('/getNewUser', methods=['GET'])
def getNewUser():
    return render_template('public/register.html')


@app.route('/register', methods=['POST'])
def register():
    get_data = request.get_json()
    db = Database()
    db.cursor.execute("select * from vein.account where user_id='{}'".format(
        get_data["id"]
    ))
    row = db.cursor.fetchone()
    password = md5_secret(get_data["password"])
    if not row:
        db.cursor.execute("insert into vein.account values('{}', '{}', '{}', '0')".format(
            get_data["id"], password, get_data["username"]
        ))
        os.mkdir("./users/{}".format(get_data["id"]))
        os.mkdir("./users/{}/vein".format(get_data["id"]))
        os.mkdir("./users/{}/contract".format(get_data["id"]))
        return "success"
    else:
        return "error"


@app.route('/login', methods=['POST'])
def login():
    get_data = request.get_json()
    session['user_id'] = get_data['username']
    db = Database()
    db.cursor.execute("select * from vein.account where user_id='{}'".format(get_data['username']))
    row = db.cursor.fetchone()
    if not row:
        return "error"
    elif row[1] == md5_secret(get_data['password']):
        if row[3] == '0':
            return "no vein"
        else:
            return "success"
    else:
        return "error"


@app.route('/getContract', methods=['GET', 'POST'])
def getContract():
    if request.method == 'GET':
        return render_template("public/contract.html")


@app.route('/getSymbolInfo', methods=['POST'])
def getSymbolInfo():
    db = Database()
    dic = {}
    db.cursor.execute("select * from vein.account where user_id != '{}'".format(session["user_id"]))
    dic['userInfo'] = to_list(db.cursor)
    db.cursor.execute("select * from vein.contract where user_id='{}'".format(session["user_id"]))
    dic['contractInfo'] = to_list(db.cursor)
    return json.dumps(dic)


@app.route('/uploadSignRequest', methods=['POST'])
def uploadSignRequest():
    file = request.files['vein_image']
    # 检查指静脉是否匹配
    ret = vein_matching(file, session['user_id'])
    if not ret[0]:
        return "matching error"
    suffix = os.path.splitext(file.filename)[-1]
    contract_name = request.form['contract_name']
    # 保存文件（指静脉、合同等）至contract文件夹
    db = Database()
    db.cursor.execute("select * from vein.contract where user_id='{}' and name='{}'".format(
        session['user_id'], contract_name
    ))
    # 如果合同路径不存在，需要新建文件夹
    contract_id = db.cursor.fetchone()[0]
    if not pathlib.Path("./contract/{}".format(contract_id)).is_dir():
        os.mkdir("./contract/{}".format(contract_id))
    # 新建"甲方id_乙方id"文件夹
    target_id = request.form['target_id']
    os.mkdir("./contract/{}/{}".format(contract_id, session['user_id'] + '_' + target_id))
    # 将合同保存在该文件夹中
    shutil.copyfile(
        "./users/{}/contract/{}".format(session['user_id'], contract_name),
        "./contract/{}/{}/{}".format(contract_id, session['user_id'] + '_' + target_id, contract_name)
    )
    # 将指静脉也保存在此文件夹中
    cv2.imwrite(
        "./contract/{}/{}/{}".format(contract_id, session['user_id'] + '_' + target_id, session['user_id'] + suffix),
        ret[1]
    )
    # 新建json文件以便保存一些有关信息
    db.cursor.execute("select * from vein.account where user_id='{}'".format(session['user_id']))
    first_name = db.cursor.fetchone()[2]
    # 将图片记录为base64
    f = open(
        "./contract/{}/{}/{}".format(contract_id, session['user_id'] + '_' + target_id, session['user_id'] + suffix),
        "rb")
    image_data = f.read()
    f.close()
    base64_data = base64.b64encode(image_data)
    base64_data = str(base64_data, 'utf-8')

    info = {
        "first_name": first_name,
        "first_id": session['user_id'],
        "first_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        "first_vein": base64_data,
        "first_feature": str(ret[2]).replace(' ', '').replace('[', '').replace(']', '').replace(',', ' '),
        "second_name": "",
        "second_id": "",
        "second_time": "",
        "second_vein": "",
        "second_feature": ""
    }
    f = open("./contract/{}/{}/info.json".format(contract_id, session['user_id'] + '_' + target_id), 'w',
             encoding='utf-8')
    f.write(json.dumps(info, ensure_ascii=False))
    f.close()
    # 将合同双方录入数据库
    db.cursor.execute("insert into vein.signatory values ('{}', '{}', '{}', '{}', null, null, null, null, null)".format(
        contract_id, session['user_id'], target_id, session['user_id'] + suffix
    ))
    return "success"


@app.route('/SignContract', methods=['POST'])
def SignContract():
    file = request.files['vein_image']
    # 检查指静脉是否匹配
    ret = vein_matching(file, session['user_id'])
    if not ret[0]:
        return "matching error"
    suffix = os.path.splitext(file.filename)[-1]
    contract_name = request.form['contract_name']
    target_id = request.form['target_id']
    # 获取合同id
    db = Database()
    db.cursor.execute("select * from vein.contract where user_id='{}' and name='{}'".format(
        target_id, contract_name
    ))
    contract_id = db.cursor.fetchone()[0]
    # 保存指静脉图片并记录在数据库中
    db.cursor.execute(
        "update vein.signatory set second_vein='{}' where contract_id='{}' and first_party_id='{}' and second_party_id='{}'".format(
            session['user_id'] + suffix, contract_id, target_id, session['user_id']
        ))
    cv2.imwrite(
        "./contract/{}/{}/{}".format(contract_id, target_id + '_' + session['user_id'], session['user_id'] + suffix),
        ret[1]
    )
    # 获取指静脉的base64编码
    f = open(
        "./contract/{}/{}/{}".format(contract_id, target_id + '_' + session['user_id'], session['user_id'] + suffix),
        "rb")
    image_data = f.read()
    f.close()
    base64_data = base64.b64encode(image_data)
    base64_data = str(base64_data, 'utf-8')
    # 修改json文件
    f1 = open("./contract/{}/{}/info.json".format(contract_id, target_id + '_' + session['user_id']), 'r',
              encoding='utf-8')
    content = json.loads(f1.read())
    f1.close()
    db.cursor.execute("select * from vein.account where user_id='{}'".format(session['user_id']))
    second_name = db.cursor.fetchone()[2]
    content['second_name'] = second_name
    content['second_id'] = session['user_id']
    content['second_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    content['second_vein'] = base64_data
    content['second_feature'] = str(ret[2]).replace(' ', '').replace('[', '').replace(']', '').replace(',', ' ')
    f2 = open("./contract/{}/{}/info.json".format(contract_id, target_id + '_' + session['user_id']), 'w',
              encoding='utf-8')
    f2.write(json.dumps(content, ensure_ascii=False))
    f2.close()

    # 需要生成两张二维码粘贴在合同中，分别属于双方，其中静脉信息不能共同拥有
    # 加密方式先用MD5，再用AES
    # ----------------------------first-------------------------------
    info1 = content.copy()
    info1.pop('first_vein')
    info1.pop('second_feature')
    info1.pop('second_vein')
    # md5加密
    answer = md5_secret(json.dumps(info1)).encode()
    key1 = os.urandom(16)
    iv1 = os.urandom(16)
    aes = AesCrypto(key=key1, IV=iv1)
    # AES加密
    encode = aes.encrypt(answer)
    encode = str(encode)
    # 生成二维码，保存密文
    qrObject = qrcode.QRCode()
    qrObject.add_data(encode)
    qrObject.make()
    img1 = qrObject.make_image(fill_color="red")
    path1 = './contract/{}/{}/{}_qrcode.jpg'.format(contract_id, target_id + '_' + session['user_id'], target_id)
    with open(path1, 'wb') as f:
        img1.save(f)
        img = cv2.imread(path1)
        img = cv2.resize(img, (150, 150), interpolation=cv2.INTER_LINEAR)
        cv2.imwrite(path1, img)
    qrcode_img = Image.open(path1)
    contract_img = Image.open(
        './contract/{}/{}/{}'.format(contract_id, target_id + '_' + session['user_id'], contract_name))
    left, top = findQrcodeLoc(contract_img)
    # 将二维码盖在合同中
    contract_img.paste(qrcode_img, (left, contract_img.size[1] - top))
    contract_img.save(
        './contract/{}/{}/{}'.format(contract_id, target_id + '_' + session['user_id'],
                                     target_id + "finish" + contract_name))
    # -----------------------------second-------------------------------
    info2 = content.copy()
    info2.pop('first_feature')
    info2.pop('first_vein')
    info2.pop('second_vein')
    # 将"want to get info"加密生成二维码，将key、iv保存在数据库中，二维码应盖在合同中
    answer = md5_secret(json.dumps(info2)).encode()
    key2 = os.urandom(16)
    iv2 = os.urandom(16)
    aes = AesCrypto(key=key2, IV=iv2)
    encode = aes.encrypt(answer)
    encode = str(encode)
    # 生成二维码，保存密文
    qrObject = qrcode.QRCode()
    qrObject.add_data(encode)
    qrObject.make()
    img2 = qrObject.make_image(fill_color="red")
    path2 = './contract/{}/{}/{}_qrcode.jpg'.format(contract_id, target_id + '_' + session['user_id'],
                                                    session['user_id'])
    with open(path2, 'wb') as f:
        img2.save(f)
        img = cv2.imread(path2)
        img = cv2.resize(img, (150, 150), interpolation=cv2.INTER_LINEAR)
        cv2.imwrite(path2, img)
    qrcode_img = Image.open(path2)
    contract_img = Image.open(
        './contract/{}/{}/{}'.format(contract_id, target_id + '_' + session['user_id'], contract_name))
    left, top = findQrcodeLoc(contract_img)
    contract_img.paste(qrcode_img, (left, contract_img.size[1] - top))
    contract_img.save(
        './contract/{}/{}/{}'.format(contract_id, target_id + '_' + session['user_id'],
                                     session['user_id'] + "finish" + contract_name))
    # 将key、iv加入数据库(注意key和iv中可能包含单引号或斜杠)
    key1 = str(key1).replace("'", "''").replace("\\", "\\\\")
    iv1 = str(iv1).replace("'", "''").replace("\\", "\\\\")
    key2 = str(key2).replace("'", "''").replace("\\", "\\\\")
    iv2 = str(iv2).replace("'", "''").replace("\\", "\\\\")

    db.cursor.execute("update vein.signatory set first_k='{}', first_iv='{}', second_k='{}', second_iv='{}' "
                      "where contract_id='{}' and first_party_id='{}' and second_party_id='{}'".format(
        key1, iv1, key2, iv2, contract_id, target_id, session['user_id']
    ))
    return "success"


@app.route('/uploadContract', methods=['POST'])
def uploadContract():
    # 将图片保存在users/upload_contract目录下
    file = request.files.get('contract')
    suffix = os.path.splitext(file.filename)[-1]
    filename = os.path.splitext(file.filename)[0]
    nowTime = calendar.timegm(time.gmtime())
    # 保存之前检查用户是否上传同名文件
    db = Database()
    db.cursor.execute("select * from vein.contract where name='{}'".format(filename))
    row = db.cursor.fetchone()
    if not row:
        file.save("./users/{}/contract/".format(session['user_id']) + filename + suffix)
        # 图片路径和名称应该保存在数据库中
        db.cursor.execute("insert into vein.contract values ('{}', '{}', '{}')".format(
            nowTime, session['user_id'], filename + suffix
        ))
        return "success"
    else:
        return "error"


@app.route('/uploadVein', methods=['POST'])
def uploadVein():
    file = request.files.get('vein')
    suffix = os.path.splitext(file.filename)[-1]
    file.save("./users/{}/vein/".format(session['user_id']) + "vein" + suffix)
    db = Database()
    db.cursor.execute("update vein.account set vein='{}' where user_id='{}'".format(
        "vein" + suffix, session['user_id']
    ))
    return "success"


@app.route('/getExistSignatory', methods=['POST'])
def getExistSignatory():
    # 查询所有user_id和姓名、contract_id和合同名称对应情况
    db = Database()
    db.cursor.execute("select * from vein.account")
    db_account = to_list(db.cursor)
    account = {}
    for i in db_account:
        account[i["user_id"]] = i["name"]
    db.cursor.execute("select * from vein.contract")
    db_contract = to_list(db.cursor)
    contract = {}
    for i in db_contract:
        contract[i["contract_id"]] = i["name"]
    result = {
        "user_id": session['user_id'],
        "finish": [],
        "waitme": [],
        "waitother": []
    }

    # 获取finish，若甲乙方均上传指静脉图片，并且当前客户为甲方或乙方，说明该合同为属于当前客户并且状态为已签署
    db.cursor.execute(
        "select * from vein.signatory "
        "where first_vein is not null "
        "and second_vein is not null "
        "and (first_party_id = '{}' or second_party_id = '{}')".format(
            session['user_id'], session['user_id'])
    )
    result['finish'] = to_list(db.cursor)
    for i in result['finish']:
        i["contract_name"] = contract[i["contract_id"]]
        i["first_name"] = account[i["first_party_id"]]
        i["second_name"] = account[i["second_party_id"]]
    # 获取waitme，若当前客户为乙方，并且还未上传指静脉图片，说明该合同属于当前客户并且状态为待签署
    db.cursor.execute(
        "select * from vein.signatory "
        "where second_party_id='{}' "
        "and second_vein is null".format(session['user_id'])
    )
    result['waitme'] = to_list(db.cursor)
    for i in result['waitme']:
        i["contract_name"] = contract[i["contract_id"]]
        i["first_name"] = account[i["first_party_id"]]
        i["second_name"] = account[i["second_party_id"]]
    # 获取waitother
    db.cursor.execute(
        "select * from vein.signatory "
        "where first_party_id='{}' "
        "and second_vein is null".format(session['user_id'])
    )
    result['waitother'] = to_list(db.cursor)
    for i in result['waitother']:
        i["contract_name"] = contract[i["contract_id"]]
        i["first_name"] = account[i["first_party_id"]]
        i["second_name"] = account[i["second_party_id"]]
    return json.dumps(result)


@app.route('/preview', methods=['POST', 'GET'])
def preview():
    if request.method == "POST":
        get_data = request.get_json()
        db = Database()
        my_id = session['user_id']
        if get_data['mode'] == "已签署":
            first_party_id = ""
            second_party_id = ""
            contract_id = ""
            db.cursor.execute(
                "select * from vein.contract where user_id='{}' and name='{}'".format(
                    my_id, get_data['contract_name']
                )
            )
            result = to_list(db.cursor)
            if len(result) == 0:
                db.cursor.execute(
                    "select * from vein.contract where user_id='{}' and name='{}'".format(
                        get_data['target_id'], get_data['contract_name']
                    )
                )
                result = to_list(db.cursor)
                first_party_id = get_data['target_id']
                second_party_id = my_id
                contract_id = result[0]['contract_id']
            else:
                first_party_id = my_id
                second_party_id = get_data['target_id']
                contract_id = result[0]['contract_id']
            path = "./contract/" + contract_id + "/" + first_party_id + "_" + second_party_id + "/" + my_id + "finish" + get_data['contract_name']
            session['path'] = path
            return "success"
        else:
            if get_data['mode'] == "待对方签署":
                path = "./users/" + my_id + "/contract/" + get_data['contract_name']
            else:
                path = "./users/" + get_data['target_id'] + "/contract/" + get_data['contract_name']
            session['path'] = path
            return "success"
    else:
        return send_file(session['path'])


@app.route('/scan', methods=['POST', 'GET'])
def scan():
    if request.method == 'GET':
        return render_template("public/info.html")
    else:
        # 使用密钥判断MD5是否相同
        db = Database()
        get_data = request.get_json()
        my_id = session['user_id']
        target_id = get_data['target_id']
        contract_name = get_data['contract_name']
        db.cursor.execute(
            "select * from vein.contract where user_id='{}' and name='{}'".format(
                my_id, contract_name
            )
        )
        result = to_list(db.cursor)
        if len(result) == 0:
            db.cursor.execute(
                "select * from vein.contract where user_id='{}' and name='{}'".format(
                    target_id, contract_name
                )
            )
            result = to_list(db.cursor)
            first_party_id = target_id
            second_party_id = my_id
            contract_id = result[0]['contract_id']
        else:
            first_party_id = my_id
            second_party_id = target_id
            contract_id = result[0]['contract_id']
        info_path = "./contract/" + contract_id + "/" + first_party_id + "_" + second_party_id
        db.cursor.execute(
            "select * from vein.signatory where contract_id='{}' and first_party_id='{}' and second_party_id='{}'".format(
                contract_id, first_party_id, second_party_id
            )
        )
        result = to_list(db.cursor)
        first_k = result[0]['first_k']
        first_iv = result[0]['first_iv']
        second_k = result[0]['second_k']
        second_iv = result[0]['second_iv']
        # 读取info.json获得原本的信息
        f = open(info_path + "/" + "info.json", 'r', encoding='utf-8')
        content = json.loads(f.read())
        f.close()
        # 扫描二维码获得加密的信息
        filename = info_path + "/" + my_id + "_qrcode.jpg"
        # 包含中文路径的话需要处理
        # image = cv2.imdecode(np.fromfile(filename, dtype=np.uint8), -1)
        # detector = cv2.QRCodeDetector()
        # data, vertices_array, binary_qrcode = detector.detectAndDecode(image)
        reader = zxing.BarCodeReader()
        data = str(reader.decode(filename).parsed)

        info = content.copy()
        if my_id == first_party_id:
            info.pop('second_feature')
            info.pop('second_vein')
            info.pop('first_vein')
            if "first_finish" in info:
                info.pop('first_finish')
            if "second_finish" in info:
                info.pop('second_finish')
            k = first_k
            iv = first_iv
        else:
            info.pop('first_feature')
            info.pop('first_vein')
            info.pop('second_vein')
            if "first_finish" in info:
                info.pop('first_finish')
            if "second_finish" in info:
                info.pop('second_finish')
            k = second_k
            iv = second_iv
        # iv和k均有可能使用双引号或者单引号包裹
        if k.split("\'")[0] == 'b':
            k = k.split("\'")[1]
            k = codecs.escape_decode(k)[0]
        else:
            k = k.split("\"")[1]
            k = codecs.escape_decode(k)[0]
        if iv.split("\'")[0] == 'b':
            iv = iv.split("\'")[1]
            iv = codecs.escape_decode(iv)[0]
        else:
            iv = iv.split("\"")[1]
            iv = codecs.escape_decode(iv)[0]
        answer = md5_secret(json.dumps(info))
        pc = AesCrypto(key=k, IV=iv)
        if data is not None:
            if data.split("\'")[0] == 'b':
                data = data.split("\'")[1]
                data = codecs.escape_decode(data)[0]
            else:
                data = data.split("\"")[1]
                data = codecs.escape_decode(data)[0]
            secret = pc.decrypt(data)  # 解密数据
        else:
            return "error"
        if answer == secret:
            session["info_path"] = info_path
            # 将finish图片放入info
            f1 = open(
                session["info_path"] + "/" + first_party_id + "finish" + contract_name, "rb")
            image1_data = f1.read()
            f1.close()
            base64_data = base64.b64encode(image1_data)
            base64_data = str(base64_data, 'utf-8')
            content['first_finish'] = base64_data
            f2 = open(
                session["info_path"] + "/" + second_party_id + "finish" + contract_name, "rb")
            image2_data = f2.read()
            f2.close()
            base64_data = base64.b64encode(image2_data)
            base64_data = str(base64_data, 'utf-8')
            content['second_finish'] = base64_data

            f3 = open(session["info_path"] + "/info.json", 'w', encoding='utf-8')
            f3.write(json.dumps(content, ensure_ascii=False))
            f3.close()
            return "success"
        else:
            return "error"


@app.route('/check_info', methods=['POST'])
def check_info():
    my_id = session['user_id']
    f = open(session["info_path"] + "/" + "info.json", 'r', encoding='utf-8')
    content = json.loads(f.read())
    f.close()
    if my_id == content['first_id']:
        image = "first_finish"
    else:
        image = "second_finish"
    info = {
        "first_id": content['first_id'],
        "first_name": content['first_name'],
        "first_time": content['first_time'],
        "second_id": content['second_id'],
        "second_name": content['second_name'],
        "second_time": content['second_time'],
        "image": content[image]
    }
    return json.dumps(info)


@app.route('/personalInfo', methods=['POST'])
def personalInfo():
    result = []
    db = Database()
    db.cursor.execute("select name from vein.account where user_id='{}'".format(session['user_id']))
    row = db.cursor.fetchone()
    result.append({'name': row[0], 'userID': session['user_id']})
    return json.dumps(result)


# db = pymysql.connect(host="localhost", port=3306, user="dtj", password="doutianjie172915", database="vein", autocommit=True)
# cursor = db.cursor()
# cursor.execute("insert into vein.account values('123', 'dtj')")
# cursor.execute("delete from vein.account where userid='123'")
def vein_matching(img1, user_id):
    # 首先保存为临时文件，再使用os读入
    suffix = os.path.splitext(img1.filename)[-1]
    path = "./tempfile/" + session['user_id'] + suffix
    img1.save(path)
    origin = cv2.imread("./tempfile/" + session['user_id'] + suffix, cv2.IMREAD_GRAYSCALE)
    os.remove(path)
    # 找到用户注册时上传的指纹文件进行匹配
    db = Database()
    db.cursor.execute("select * from vein.account where user_id='{}'".format(user_id))
    vein_name = db.cursor.fetchone()[3]
    img2 = cv2.imread("./users/{}/vein/{}".format(user_id, vein_name), cv2.IMREAD_GRAYSCALE)
    # 开始匹配
    # INTER_NEAREST INTER_LINEAR INTER_AREA INTER_CUBIC INTER_LANCZOS4
    img1 = cv2.resize(origin, (40, 120), interpolation=cv2.INTER_LINEAR)
    img2 = cv2.resize(img2, (40, 120), interpolation=cv2.INTER_LINEAR)
    img1 = clahe(img1, 2, 2)      # clahe图像优化
    img2 = clahe(img2, 2, 2)
    img1 = guass(img1)            # 滤波
    img2 = guass(img2)
    img1 = clahe(img1, 2, 2)      # clahe图像优化
    img2 = clahe(img2, 2, 2)
    img1 = scharr(img1)           # 边缘检测
    img2 = scharr(img2)
    img1 = cv2.equalizeHist(img1) # 直方图均衡化
    img2 = cv2.equalizeHist(img2)
    img1 = clahe(img1, 2, 1)      # clahe图像优化
    img2 = clahe(img2, 2, 1)
    img1, kp1, des1 = sift(img1)  # 特征点提取
    img2, kp2, des2 = sift(img2)

    index_params = dict(algorithm=0, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    # 准备一个空的掩膜来绘制好的匹配
    mask_matches = [[0, 0] for i in range(len(matches))]
    # 向掩膜中添加数据
    matching_points = 0
    # 记录匹配到的点的信息
    img1_pts = []
    for i, (m, n) in enumerate(matches):
        if m.distance < 0.7 * n.distance:
            mask_matches[i] = [1, 0]
            matching_points += 1
            img1_pts.append(kp1[m.queryIdx])
    img1_info = []
    for kp in img1_pts:
        info = [kp.angle, kp.octave, kp.pt, kp.response, kp.size]
        img1_info.append(info)
    if matching_points >= 6:
        return True, origin, img1_info
    else:
        return False, origin, img1_info


def findQrcodeLoc(contract_img):
    text = pytesseract.image_to_boxes(contract_img, output_type=Output.DICT, lang='chi_sim')
    pos = {}
    for i in range(0, len(text['char']) - 6):
        if text['char'][i] == '%' and text['char'][i + 1] == "在" and text['char'][i + 2] == "此" and text['char'][
            i + 3] == "处" and text['char'][i + 4] == "盖" and text['char'][i + 5] == "章":
            pos["%"] = (text['left'][i], text['top'][i])
            pos["在"] = (text['left'][i + 1], text['top'][i + 1])
            pos["此"] = (text['left'][i + 2], text['top'][i + 2])
            pos["处"] = (text['left'][i + 3], text['top'][i + 3])
            pos["盖"] = (text['left'][i + 4], text['top'][i + 4])
            pos["章"] = (text['left'][i + 5], text['top'][i + 5])
    return pos["%"]


def show_img(title, image):
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def scharr(img):
    x = cv2.Scharr(img, cv2.CV_16S, 1, 0)
    y = cv2.Scharr(img, cv2.CV_16S, 0, 1)
    absX = cv2.convertScaleAbs(x)
    absY = cv2.convertScaleAbs(y)
    img = cv2.addWeighted(absX, 1, absY, 0, 0)
    return img


def sift(img):
    s = cv2.SIFT_create()
    kp, des = s.detectAndCompute(img, None)
    return img, kp, des


def guass(img):
    # 高斯滤波
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    return blur


def clahe(img, x, n):
    # clahe均衡化
    clahe = cv2.createCLAHE(clipLimit=n, tileGridSize=(x, x))
    img = clahe.apply(img)
    return img


def show_two_image(img1, img2):
    imgs = np.hstack([img1, img2])
    show_img('1', imgs)


def md5_secret(s):
    hl = hashlib.md5()
    hl.update(s.encode(encoding='utf-8'))
    return hl.hexdigest()


def to_list(cursor):
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor:
        results.append(dict(zip(columns, row)))
    return results


class Database:
    def __init__(self):
        self.db = pymysql.connect(host="localhost", port=3306, user="dtj", password="doutianjie172915", database="vein",
                                  autocommit=True)
        self.cursor = self.db.cursor()

    def __del__(self):
        self.cursor.close()
        self.db.close()


class AesCrypto:
    def __init__(self, key, IV):
        self.key = key
        self.iv = IV
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


if __name__ == '__main__':
    app.run(port=5000)
