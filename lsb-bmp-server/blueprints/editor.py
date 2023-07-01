from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os

from util.lsb import *

bp = Blueprint('editor', __name__, url_prefix='/editor')
now_dir = os.path.realpath(__file__)
uploads_dir = os.path.dirname(os.path.dirname(now_dir))
UPLOAD_FOLDER = os.path.join(uploads_dir, 'uploads')


@bp.route('/submit-lsb', methods=['POST'])
def submit_article():
    data = request.json
    filename = data['filename']  # 上传的文件名 用于读取文件 也是需要嵌入的图片
    info = data['info']  # 嵌入的信息

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    code, filename = if_can_be_process(filepath, info, True, filename, True)

    if code == 0:
        return {
            'code': 0,
            'msg': 'success',
            'data': {
                "url": "http://localhost:5000/uploads/" + filename,
            }
        }
    else:
        return {
            'code': code,
            'msg': filename,
            'data': {}
        }


@bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {
            "code": 400,
            "msg": "No file part"
        }
    file = request.files['file']
    type = request.args.get('type')

    # filename = secure_filename(file.filename)
    filename = file.filename

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    if type == 'embed':  # 如果是嵌入图片 只处理一下可嵌入的信息长度就可以
        max_bits = get_max(filepath)
        main_max_lsb_length = "{} bits".format(max_bits)
        sub_max_lsb_length = "{}个字符 for ASCII 字符串 \n{}个字符 for utf-16编码字符串（汉字）\n{}个字符 for utf-32编码字符串（稀有字符，如emoji）\n".format(
            math.floor(max_bits / 8), math.floor(max_bits / 16), math.floor(max_bits / 32))

        return {
            "code": 0,
            "data": {
                "filename": filename,
                "url": "http://localhost:5000/uploads/" + filename,
                "main_max_lsb_length": main_max_lsb_length,
                "sub_max_lsb_length": sub_max_lsb_length
            },
            "msg": 'File uploaded successfully'
        }

    else:  # 如果是提取信息
        code, info = come_on(filepath, True)

        if code != 0:
            return {
                "code": code,
                "data": {},
                "msg": info
            }
        else:
            return {
                "code": 0,
                "data": {
                    "info": info
                },
                "msg": 'File decoded successfully'
            }
