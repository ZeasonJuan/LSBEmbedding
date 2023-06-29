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
    filepath = 'uploads/' + filename
    # TODO ... Lsb的处理
    filename = if_can_be_process(filepath, info, True)
    # TODO 接口只返回最后处理的图片url 只需要给出你最后处理完的filename是什么就行
    filename = filename

    return {
        'code': 0,
        'msg': 'success',
        'data': {
            "url": "http://localhost:5000/uploads/" + filename,
        }
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
    print(type)
    if type == 'embed':  # TODO 如果是嵌入图片 只处理一下可嵌入的信息长度就可以
        max_bits = get_max(filepath)
        max_lsb_length = "{}个字符 for ASCII 字符串 \n{}个字符 for utf-16编码字符串（汉字）\n{}个字符 for utf-32编码字符串（稀有字符，如emoji）\n总共{}位".format(
            math.floor(max_bits / 8), math.floor(max_bits / 16), math.floor(max_bits / 32), max_bits)
        # TODO 这里处理一下lsb的长度限制 返回一个字节数或者怎么样的
        # TODO 因为前端不做判断 这里就写个str就行了

        # TODO ... 处理lsb长度的方法

        return {
            "code": 0,
            "data": {
                "filename": filename,
                "url": "http://localhost:5000/uploads/" + filename,
                "max_lsb_length": max_lsb_length
            },
            "msg": 'File uploaded successfully'
        }

    else:  # TODO 如果是解密图片
        info = come_on(filepath)
        # TODO ... 处理lsb的解密
        # TODO 这里的结果就写个str就行了

        return {
            "code": 0,
            "data": {
                "info": info
            },
            "msg": 'File decoded successfully'
        }
