import time

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import gzip
import hashlib
import math
import random
import struct
import sys
import numpy as np
MY_FINAL_KEY = "阮在胜是阮在胜是阮在胜是阮在胜是阮在胜是阮在胜是阮在胜是阮在胜是阮在胜是阮在胜是阮在胜"
MY_FINAL_KEY = MY_FINAL_KEY.encode('utf-32')
#python 的 string会比内容多那么几十byte，有大问题
#判断出字符串中的最大字符类型1byte 2byte 4byte 从而计算字符串长度

#6/20更新，计算长度后与压缩进行对比，谁小用谁。返回值修改为1.是否使用压缩2.string的encode方式3.字节流变成的数组
#若使用压缩，返回字节流变成的数字流（0-255）（可以直接用写完的那个方法转成list）
#若不适用压缩，返回大数字流（根据utf32/16变化）（重新写一个方法，接收encode方法参数）
dict_encode_method_and_its_bit_amount = {"utf-32": 32, "utf-16": 16, 'ascii': 8}
def is_bmp(filepath):
    with open(filepath, 'rb') as f:
        header = f.read(14)
        header_duple = struct.unpack('<2sI2HI', header)
        return header_duple[0] == b'BM'
def encrypt(array, key):
    seed = int.from_bytes(hashlib.sha256(key).digest(), 'big')
    random_machine = np.random.default_rng(seed)
    roll = random_machine.permutation(len(array))
    return array[roll]

def decrypt(roll_array, key):
    seed = int.from_bytes(hashlib.sha256(key).digest(), 'big')
    random_machine = np.random.default_rng(seed)
    roll = random_machine.permutation(len(roll_array))
    empty_array = np.empty_like(roll_array)
    empty_array[roll] = roll_array
    return empty_array
def size_of_string(a_str):
    if isinstance(a_str, str):
        #找出最大的字符
        max_character = 0
        for one_character in a_str:
            max_character = max(max_character, sys.getsizeof(one_character))


        if max_character == 50:
            unzip_size = len(a_str)
            zip_byte = gzip.compress(a_str.encode('ascii'))

            zip_size = sys.getsizeof(zip_byte)
            if zip_size < unzip_size:
                return True, 'ascii', [i for i in zip_byte]
            else:
                return False, 'ascii', [ord(i) for i in a_str]
        elif max_character == 76:
            unzip_size = len(a_str) * 2
            zip_byte = gzip.compress(a_str.encode('utf-16'))

            zip_size = sys.getsizeof(zip_byte)
            print(unzip_size, zip_size)
            if zip_size < unzip_size:
                return True, 'utf-16', [i for i in zip_byte]
            else:
                return False, 'utf-16', [ord(i) for i in a_str]
        else:
            unzip_size = len(a_str) * 4
            zip_byte = gzip.compress(a_str.encode('utf-32'))

            zip_size = sys.getsizeof(zip_byte)
            if zip_size < unzip_size:
                return True, 'utf-32', [i for i in zip_byte]
            else:
                return False, 'utf-32', [ord(i) for i in a_str]
    else:
        return "Not a string!"
def list_to_number(a_list):
    if len(a_list) != 8 and len(a_list) != 16 and len(a_list) != 32:
        return "not a character"
    a_list.reverse()
    the_sum = 0
    for i in range(len(a_list)):
        the_sum += a_list[i] * (2 ** i)
    return the_sum

#把数字转为二进制，同时变成一个列表
def transform_number_to_list(number):
    if not isinstance(number, int) or number > 255 or number < 0:
        return "Pixel number must be integrate between 0-255"
    final_list = []
    while number != 0:
        this_digit = number % 2
        final_list.append(this_digit)
        number = math.floor(number / 2)

    while len(final_list) != 8:
        final_list.append(0)
    final_list.reverse()
    return final_list


#大数版本
def transform_utf_to_list(number, bit_number):
    final_list = []
    while number != 0:
        this_digit = number % 2
        final_list.append(this_digit)
        number = math.floor(number / 2)

    while len(final_list) != bit_number:
        final_list.append(0)
    final_list.reverse()
    return final_list


#把信息的0-1数组补全，让它的长度和LSB嵌入的最大
def get_lsb(linear_list, width, height, bibi_count):
    #linear_list += [0] * (width * height - len(linear_list))
    #这里可以加个加密
    lsb_new = []
    long_linear = linear_list + [0] * (height * width - len(linear_list)) if bibi_count == 8 else linear_list + [0] * (3 * height * width - len(linear_list))
    long_linear = encrypt(np.array(long_linear), MY_FINAL_KEY).tolist()
    if bibi_count == 8:
        for i in range(height):
            this_line = []
            for j in range(width):
                element = long_linear[i * width + j] #if i * width + j < len(linear_list) else 0
                this_line.append(element)
            lsb_new.append(this_line)
    else:
        for z in range(3):
            this_page = []
            for i in range(height):
                this_line = []
                for j in range(width):
                    element = long_linear[z * (width * height) + i * width + j] #if z * (width * height) + i * width + j < len(linear_list) else 0
                    this_line.append(element)
                this_page.append(this_line)
            lsb_new.append(this_page)
    return lsb_new

def get_max(filepath):
    with open(filepath, 'rb') as f:
        binary_header = f.read(14)
        binary_message = f.read(40)
        header_duple = struct.unpack('<2sI2HI', binary_header)
        message_duple = struct.unpack('3I2H6I', binary_message)
        bibicount = message_duple[4]
        width = message_duple[1]
        height = message_duple[2]

        max_page_bits = width * height if bibicount == 8 else width * height * 3
        return max_page_bits
def come_on(filepath):
    with open(filepath, 'rb') as f:
        binary_header = f.read(14)
        binary_message = f.read(40)
        header_duple = struct.unpack('<2sI2HI', binary_header)
        message_duple = struct.unpack('3I2H6I', binary_message)
        print(header_duple, message_duple)
        encode_method = ''
        if header_duple[2] == header_duple[3] == 0:
            return "Not Encrypt!"
        elif header_duple[2] == 0:
            encode_method = 'ascii'
        elif header_duple[3] == 0:
            encode_method = 'utf-16'
        else:
            encode_method = 'utf-32'

        bibi_count = message_duple[4]
        width = message_duple[1]
        height = message_duple[2]
        is_zip = True if message_duple[3] == 1 else False
        f.seek(header_duple[-1])

        bytes_list_all = []
        for i in range(height):
            this_line_bytes = []
            for j in range(width):
                if bibi_count == 8:
                    this_pixel = int.from_bytes(f.read(1)[::-1], 'big')
                    this_line_bytes.append(transform_number_to_list(this_pixel))
                else:
                    this_pixel = []
                    this_pixel_blue = int.from_bytes(f.read(1)[::-1], 'big')
                    this_pixel_green = int.from_bytes(f.read(1)[::-1], 'big')
                    this_pixel_red = int.from_bytes(f.read(1)[::-1], 'big')
                    this_pixel.append(transform_number_to_list(this_pixel_blue))
                    this_pixel.append(transform_number_to_list(this_pixel_green))
                    this_pixel.append(transform_number_to_list(this_pixel_red))

                    this_line_bytes.append(this_pixel)
            bytes_list_all.append(this_line_bytes)
        zero_one_len = struct.unpack('<I', f.read(4))[0]

        # 转换成这个比较习惯
        bytes_list_all = np.array(bytes_list_all)
        lsb = bytes_list_all[:, :, -1] if bibi_count == 8 else bytes_list_all[:, :, :, -1].transpose(2, 0, 1)
        print(lsb.shape)
        zero_one_list = decrypt(lsb.flatten().tolist(), MY_FINAL_KEY).tolist()[: zero_one_len]

        last_number_list = []
        print(is_zip, encode_method)
        if is_zip:
            for i in range(math.floor(len(zero_one_list) / 8)):
                last_number_list.append(list_to_number(zero_one_list[i * 8: i * 8 + 8]))
            final_msg = gzip.decompress(bytes(last_number_list)).decode(encode_method)
            return final_msg


        if not is_zip:
            chr_len = dict_encode_method_and_its_bit_amount[encode_method]
            for i in range(math.floor(len(zero_one_list) / chr_len)):
                last_number_list.append(list_to_number(zero_one_list[i * chr_len: i * chr_len + chr_len]))

            final_msg = ''
            print(last_number_list[:50])
            for i in range(len(last_number_list)):
                final_msg += chr(last_number_list[i])
            return final_msg



def if_can_be_process(filepath, embedding_string, is_noise):
    is_zip, encode_method, number_array = size_of_string(embedding_string)
    print(is_zip, number_array, encode_method)
    zero_one_list = []
    #如果是用ascii码加密，直接把数字转为列表（因为上面那个方法只适用于把1B的转为列表）
    if is_zip or encode_method == 'ascii':
        zero_one_list = [transform_number_to_list(i) for i in number_array]
    else:
        zero_one_list = [transform_utf_to_list(i, dict_encode_method_and_its_bit_amount[encode_method]) for i in number_array]

    #推平，得到一个东西
    zero_one_list = sum(zero_one_list, [])
    print(zero_one_list[:1000])

    with open(filepath, 'rb') as f:
        is_bmp = f.read(2) == b'BM'
        if not is_bmp:
            return "Not a bmp!"
        bmp_size = int.from_bytes(f.read(4)[::-1], 'big')
        bf_reserve1_is0 = int.from_bytes(f.read(2)[::-1], 'big')
        bf_reserve2_is0 = int.from_bytes(f.read(2)[::-1], 'big')
        off_bits = int.from_bytes(f.read(4)[::-1], 'big')


        this_structure_size = int.from_bytes(f.read(4)[::-1], 'big')
        width = int.from_bytes(f.read(4)[::-1], 'big')
        height = int.from_bytes(f.read(4)[::-1], 'big')
        #超过范围就不让做了
        if width > 512 or height > 512:
            return "Size too large!"

        if_bi_planes_is_1 = int.from_bytes(f.read(2)[::-1], 'big') == 1
        if not bf_reserve2_is0 == 0 or not bf_reserve1_is0 == 0 or not if_bi_planes_is_1:
            return "Something wrong with check..."
        bibi_count = int.from_bytes(f.read(2)[::-1], 'big')
        bi_compression = int.from_bytes(f.read(4)[::-1], 'big')

        bi_size_image = int.from_bytes(f.read(4)[::-1], 'big')
        bi_X_per = int.from_bytes(f.read(4)[::-1], 'big')
        bi_Y_per = int.from_bytes(f.read(4)[::-1], 'big')
        bi_color_used = int.from_bytes(f.read(4)[::-1], 'big')

        bi_coloer_important = int.from_bytes(f.read(4)[::-1], 'big')



        #如果是灰度图
        if bibi_count == 8 or bibi_count == 24:

            #判断嵌入超了吗，因为是灰度图所以不用乘三
            most_long_embedding_bytes = height * width if bibi_count == 8 else height * width * 3#三色图还得乘三
            if most_long_embedding_bytes < len(zero_one_list):
                return "Message Too large!"
            # print("这是做压缩前的嵌入信息大小", embedding_size)
            # print("这是压缩后的", sys.getsizeof(gzip.compress(embedding_string.encode('utf-8'))))
            #
            # embedding_string_to_bytes = embedding_string.encode('ascii')
            # print("这是变成byte后的大小", sys.getsizeof(embedding_string_to_bytes), embedding_string_to_bytes)
            # if most_long_embedding_bytes < embedding_size:
            #     return "Embedding too large!"


            # 调色盘
            color_plate = []
            if bibi_count == 8:
                for i in range(256):
                    one_in_color_plate = []
                    rgb_blue = int.from_bytes(f.read(1)[::-1], 'big')
                    rgb_green = int.from_bytes(f.read(1)[::-1], 'big')
                    rgb_red = int.from_bytes(f.read(1)[::-1], 'big')
                    one_in_color_plate.append(rgb_blue)
                    one_in_color_plate.append(rgb_green)
                    one_in_color_plate.append(rgb_red)

                    color_plate.append(one_in_color_plate)
                    must_be_zero = int.from_bytes(f.read(1)[::-1], 'big')
                    if must_be_zero != 0:
                        return "Color plate error..."



            f.seek(off_bits)
            # 将图片读入

            bytes_list_all = []
            for i in range(height):
                this_line_bytes = []
                for j in range(width):
                    if bibi_count == 8:
                        this_pixel = int.from_bytes(f.read(1)[::-1], 'big')
                        this_line_bytes.append(transform_number_to_list(this_pixel))
                    else:
                        this_pixel = []
                        this_pixel_blue = int.from_bytes(f.read(1)[::-1], 'big')
                        this_pixel_green = int.from_bytes(f.read(1)[::-1], 'big')
                        this_pixel_red = int.from_bytes(f.read(1)[::-1], 'big')
                        this_pixel.append(transform_number_to_list(this_pixel_blue))
                        this_pixel.append(transform_number_to_list(this_pixel_green))
                        this_pixel.append(transform_number_to_list(this_pixel_red))

                        this_line_bytes.append(this_pixel)
                bytes_list_all.append(this_line_bytes)

            #转换成这个比较习惯
            bytes_list_all = np.array(bytes_list_all)
            print(bytes_list_all.shape)
            new_lsb = np.array(get_lsb(zero_one_list, width=width, height=height, bibi_count=bibi_count))
            print(new_lsb.shape)

            if bibi_count == 8:
                bytes_list_all[:, :, -1] = new_lsb
                if is_noise:
                    bytes_list_all[:, :, -np.random.randint(2, 5)] = np.random.randint(0, 2, (height, width))
            else:
                for i in range(3):
                    bytes_list_all[:, :, i, -1] = new_lsb[i, :, :]
                    if is_noise:
                        bytes_list_all[:, :, i, -np.random.randint(2, 5)] = np.random.randint(0, 2, (height, width))


            #得到最后的bitmap
            result = bytes_list_all.tolist()
            if bibi_count == 8:
                for i in range(height):
                    for j in range(width):
                        result[i][j] = list_to_number(result[i][j])
            else:
                for i in range(height):
                    for j in range(width):
                        for k in range(3):
                            result[i][j][k] = list_to_number(result[i][j][k])


            #开始写
            final_filename = 'output_{}.bmp'.format(int(time.time()))
            with open("uploads/" + final_filename, 'wb') as fw:
                #如果两个都是0说明是没有替换的
                if encode_method == "ascii":
                    fw.write(struct.pack('<2sI2HI', b'BM', bmp_size, 0, 1, off_bits))
                elif encode_method == "utf-16":
                    fw.write(struct.pack('<2sI2HI', b'BM', bmp_size, 1, 0, off_bits))
                else:
                    fw.write(struct.pack('<2sI2HI', b'BM', bmp_size, 1, 1, off_bits))

                #这个判断是否压缩
                if is_zip:
                    fw.write(struct.pack('<3I2H6I', this_structure_size, width, height, 1, bibi_count, bi_compression, bi_size_image,
                                     bi_X_per, bi_Y_per, bi_color_used, bi_coloer_important))
                else:
                    fw.write(struct.pack('<3I2H6I', this_structure_size, width, height, 0, bibi_count, bi_compression,
                                         bi_size_image,
                                         bi_X_per, bi_Y_per, bi_color_used, bi_coloer_important))
                if bibi_count == 8:
                    for i in range(256):
                        fw.write(struct.pack('<4B', color_plate[i][0], color_plate[i][1],
                                             color_plate[i][2], 0))
                    for i in range(height):
                        for j in range(width):
                            fw.write(struct.pack('<B', result[i][j]))
                else:
                    for i in range(height):
                        for j in range(width):
                            for k in range(3):
                                fw.write(struct.pack('<B', result[i][j][k]))
                fw.write(struct.pack('<I', len(zero_one_list)))
                return final_filename

bp = Blueprint('editor', __name__, url_prefix='/editor')
now_dir = os.path.realpath(__file__)
uploads_dir = os.path.dirname(os.path.dirname(now_dir))
UPLOAD_FOLDER = os.path.join(uploads_dir, 'uploads')


@bp.route('/submit-lsb', methods=['POST'])
def submit_article():
    data = request.json
    filename = data['filename']   # 上传的文件名 用于读取文件 也是需要嵌入的图片
    info = data['info']         # 嵌入的信息
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
    if not is_bmp(filepath):
        return "Not a bmp!"

    if type == 'embed':  # TODO 如果是嵌入图片 只处理一下可嵌入的信息长度就可以
        max_bits = get_max(filepath)
        max_lsb_length = "{}个字符 for ASCII 字符串 \n{}个字符 for utf-16编码字符串（汉字）\n{}个字符 for utf-32编码字符串（稀有字符，如emoji）\n总共{}位".format(math.floor(max_bits / 8), math.floor(max_bits / 16), math.floor(max_bits / 32), max_bits)
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

