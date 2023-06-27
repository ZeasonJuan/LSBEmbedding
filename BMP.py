import gzip
import math
import struct
import sys
import numpy as np

#python 的 string会比内容多那么几十byte，有大问题
#判断出字符串中的最大字符类型1byte 2byte 4byte 从而计算字符串长度

#6/20更新，计算长度后与压缩进行对比，谁小用谁。返回值修改为1.是否使用压缩2.string的encode方式3.字节流变成的数组
#若使用压缩，返回字节流变成的数字流（0-255）（可以直接用写完的那个方法转成list）
#若不适用压缩，返回大数字流（根据utf32/16变化）（重新写一个方法，接收encode方法参数）
dict_encode_method_and_its_bit_amount = {"utf-32": 32, "utf-16": 16}
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
    if len(a_list) != 8:
        return "not a byte"
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
def get_lsb(linear_list, width, height):
    #linear_list += [0] * (width * height - len(linear_list))
    #这里可以加个加密，不太想做了嘿嘿
    lsb_new = []

    for i in range(height):
        this_line = []
        for j in range(width):
            element = linear_list[i * width + j] if i * width + j < len(linear_list) else 0
            this_line.append(element)
        lsb_new.append(this_line)
    return lsb_new



def if_can_be_process(filepath, embedding_string):
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

    with open(filepath, 'rb') as f:
        is_bmp = f.read(2) == b'BM'
        if not is_bmp:
            return "Not a bmp!"
        bmp_size = int.from_bytes(f.read(4)[::-1], 'big')
        bf_reserve1_is0 = int.from_bytes(f.read(2)[::-1], 'big') == 0
        bf_reserve2_is0 = int.from_bytes(f.read(2)[::-1], 'big') == 0
        off_bits = int.from_bytes(f.read(4)[::-1], 'big')


        this_structure_size = int.from_bytes(f.read(4)[::-1], 'big')
        width = int.from_bytes(f.read(4)[::-1], 'big')
        height = int.from_bytes(f.read(4)[::-1], 'big')
        #超过范围就不让做了
        if width > 512 or height > 512:
            return "Size too large!"

        if_bi_planes_is_1 = int.from_bytes(f.read(2)[::-1], 'big') == 1
        if not bf_reserve2_is0 or not bf_reserve1_is0 or not if_bi_planes_is_1:
            return "Something wrong with check..."
        bibi_count = int.from_bytes(f.read(2)[::-1], 'big')
        bi_compression = int.from_bytes(f.read(4)[::-1], 'big')

        no_use = f.read(16)

        bi_coloer_important = int.from_bytes(f.read(4)[::-1], 'big')



        #如果是灰度图
        if bibi_count == 8:

            #判断嵌入超了吗，因为是灰度图所以不用乘三
            most_long_embedding_bytes = height * width#三色图还得乘三
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
                    this_pixel = int.from_bytes(f.read(1)[::-1], 'big')
                    this_line_bytes.append(transform_number_to_list(this_pixel))
                bytes_list_all.append(this_line_bytes)

            #转换成这个比较习惯
            bytes_list_all = np.array(bytes_list_all)

            LSB = bytes_list_all[:, :, -1]
            new_lsb = np.array(get_lsb(zero_one_list, width=width, height=height))
            bytes_list_all[:, :, -1] = new_lsb


            #得到最后的bitmap
            result = bytes_list_all.tolist()
            for i in range(height):
                for j in range(width):
                    result[i][j] = list_to_number(result[i][j])

            #开始写
            with open('output.bmp', 'wb') as fw:
                fw.write(struct.pack('<2sI2I', 'BM', bmp_size))

        print(width, height, bibi_count, off_bits, must_be_zero)

if_can_be_process("../data/可供选用的图片/可供选用的图片/256灰度/test2.bmp", '😀')