import random
import os
import random
import string
import csv
import pandas as pd
import numpy as np
from PIL import Image
from lsb import *
import os

now_dir = os.path.realpath(__file__)
uploads_dir = os.path.dirname(os.path.dirname(now_dir))
UPLOAD_FOLDER = os.path.join(uploads_dir, 'uploads')

IS_NOISE = False
NEED_ENCRYPT = False


def test_crop_resilience(image_path, direction, cut_pixel_count, step=1):
    image = Image.open(image_path)
    width, height = image.size

    # Determine the direction to crop
    if direction in ['x', 'xy']:
        start_x0 = 0
        end_x0 = cut_pixel_count + 1
        remaining_width = width - cut_pixel_count
    if direction in ['y', 'xy']:
        start_y0 = 0
        end_y0 = cut_pixel_count + 1
        remaining_height = height - cut_pixel_count

    # Crop the image in all possible ways and test if the message can still be extracted
    if direction == 'x':
        for i in range(start_x0, end_x0, step):
            cropped_image_path = image_path[:-4] + f"_cropped_at_x_({i}_0_{remaining_width}_{height}).bmp"
            crop_image(image_path, cropped_image_path, i, 0, remaining_width, height)
            try_to_extract_message(cropped_image_path)

    if direction == 'y':
        for i in range(start_y0, end_y0, step):
            cropped_image_path = image_path[:-4] + f"_cropped_at_y_(0_{i}_{width}_{remaining_height}).bmp"
            crop_image(image_path, cropped_image_path, 0, i, width, remaining_height)
            try_to_extract_message(cropped_image_path)

    if direction == 'xy':
        for i in range(start_x0, end_x0, step):
            for j in range(start_y0, end_y0, step):
                cropped_image_path = image_path[
                                     :-4] + f"_cropped_at_xy_({i}_{j}_{remaining_width}_{remaining_height}).bmp"
                crop_image(image_path, cropped_image_path, i, j, remaining_width, remaining_height)
                try_to_extract_message(cropped_image_path)


def crop_image(image_path, cropped_image_path, start_x, start_y, width, height):
    # 打开图片
    image = Image.open(image_path)
    # 定义裁剪区域
    crop_area = (start_x, start_y, start_x + width, start_y + height)
    # 裁剪图片
    cropped_img = image.crop(crop_area)
    # 保存裁剪后的图片
    cropped_img.save(cropped_image_path)


def try_to_extract_message(cropped_image_path):
    try:
        code, message = come_on(cropped_image_path, NEED_ENCRYPT)
        if code == 0:
            print(f"Message extracted from {cropped_image_path}: {message}")
        else:
            # 删除无法提取信息的图片
            # os.remove(cropped_image_path)
            pass
    except Exception as e:
        print(f"Failed to extract message from {cropped_image_path}: {e}")
        # 删除无法提取信息的图片
        os.remove(cropped_image_path)


def patch_test_crop_resilience():
    # 读取csv文件
    df = pd.read_csv('results.csv')
    # 读取csv文件中的列
    lsb_encode_list = df['最终文件名'].tolist()
    # 拼接文件路径
    lsb_encode_list = [os.path.join(UPLOAD_FOLDER, i) for i in lsb_encode_list]
    # 调用测试函数
    for i in lsb_encode_list:
        test_crop_resilience(i, 'xy', 10)
        test_crop_resilience(i, 'x', 10)
        test_crop_resilience(i, 'y', 10)


def random_string(length, encode_mode):
    if encode_mode == 'ascii':
        letters = string.ascii_letters
        result_str = ''.join(random.choice(letters) for _ in range(length))
        return result_str
    elif encode_mode == 'utf-16':
        result_str = ''.join(chr(random.randint(0x4e00, 0x9fa5)) for _ in range(length))
        return result_str
    elif encode_mode == 'utf-32':
        emoji_list = [chr(i) for i in range(0x1F601, 0x1F64F)]
        result_str = ''.join(random.choice(emoji_list) for _ in range(length))
        return result_str
    else:
        return None


def patch_encode_test_list():
    raw_folder = "F:\\convert2bmp\\raw"
    encode_modes = ['ascii', 'utf-16', 'utf-32']
    records = []

    file_list = []
    for root, dirs, files in os.walk(raw_folder):
        for file in files:
            file_list.append(os.path.join(root, file))

    # 根据_cropped_at_{}划分文件为三份
    new_file_list = [[], [], []]
    for file in file_list:
        if "_cropped_at_80" in file:
            new_file_list[0].append(file)
        elif "_cropped_at_320" in file:
            new_file_list[1].append(file)
        elif "_cropped_at_500" in file:
            new_file_list[2].append(file)

    length_values = [1, 2, 3, 5, 10, 25, 50, 100, 250, 500, "50%", "99%"]  # lengths in bytes

    for idx, single_file_list in enumerate(new_file_list):
        file_chunks = np.array_split(single_file_list, len(encode_modes))
        for encode_mode, file_chunk in zip(encode_modes, file_chunks):
            if encode_mode == 'ascii':
                bits_per_byte = 8
            elif encode_mode == 'utf-16':
                bits_per_byte = 16
            elif encode_mode == 'utf-32':
                bits_per_byte = 32
            length_idx = 0
            for filepath in file_chunk:
                length = length_values[length_idx]
                max_length = int(get_max(filepath) / bits_per_byte)
                if length == "50%":
                    length = int(max_length * 0.5)
                elif length == "99%":
                    length = int(max_length * 0.99)
                elif length > max_length * 0.99:  # up to 99% of file size
                    print(f"File size is too small for {length} bytes. Skipping to 11...")
                    length = 11
                embedding_string = random_string(length, encode_mode)
                print(f"Now processing: File list #{idx + 1} Encoding mode: {encode_mode}, File index: {length_idx + 1}")
                status, final_filename = if_can_be_process(filepath, embedding_string, IS_NOISE,
                                                           os.path.basename(filepath), NEED_ENCRYPT)
                records.append({
                    "初始文件名": os.path.basename(filepath),
                    "最终文件名": final_filename,
                    "嵌入字符串": embedding_string,
                    "编码模式": encode_mode,
                    "编码长度": length,
                })
                length_idx += 1

    df = pd.DataFrame(records)
    df.to_csv("results.csv", index=False)


def crop_to_patch_size():
    raw_folder = "F:\\convert2bmp"
    count = 0
    phase = 0
    size_list = [80, 320, 500]
    for root, dirs, files in os.walk(raw_folder):
        for file in files:
            if count == 33:
                count = 0
                phase += 1

            file_path = os.path.join(root, file)
            img = Image.open(file_path)
            width, height = img.size
            # 根据size_list与phase确定裁剪的大小
            crop_size = size_list[phase]
            # 随机裁剪 输出大小为crop_size*crop_size
            start_x = random.randint(0, width - crop_size)
            start_y = random.randint(0, height - crop_size)
            # 将文件裁剪 并保存回原文件夹
            crop_area = (start_x, start_y, start_x + crop_size, start_y + crop_size)
            cropped_img = img.crop(crop_area)
            # 文件名写上裁剪后的大小
            cropped_img.save(file_path[:-4] + f"_cropped_at_{crop_size}.bmp")

            count += 1


class RandomEngine:
    def __init__(self, seed):
        self.seed = seed
        self.m = 2**32
        self.a = 48271
        self.c = 0

    def next(self):
        self.seed = (self.a * self.seed + self.c) % self.m
        return self.seed


if __name__ == '__main__':

    # engine = RandomEngine(seed=1)
    # print(engine.next())
    # print(engine.next())
    # print(engine.next())
    # patch_encode_test_list()
    # patch_test_crop_resilience()
    filename = "（pid=5435590）夏_cropped_at_500_output_2023-07-01-21-19-24_after_jpeg.bmp"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    try_to_extract_message(filepath)
    pass
