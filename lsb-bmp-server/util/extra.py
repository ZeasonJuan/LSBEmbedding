from PIL import Image
from util.lsb import come_on
import os

now_dir = os.path.realpath(__file__)
uploads_dir = os.path.dirname(os.path.dirname(now_dir))
UPLOAD_FOLDER = os.path.join(uploads_dir, 'uploads')


def test_crop_resilience(image_path, direction, cut_pixel_count, step=1):
    """
    Crop an image in all possible ways along both x and y directions and check if the message can still be extracted.

    Args:
        image_path (str): The path of the image to crop.
        direction (str): The direction to crop ('x', 'y', 'xy').
        cut_pixel_count (int): The number of pixels to crop.
        step (int): The step size for the cropping area. Defaults to 1.
    """
    # Load the image
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
                cropped_image_path = image_path[:-4] + f"_cropped_at_xy_({i}_{j}_{remaining_width}_{remaining_height}).bmp"
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
    # Use your existing function to extract the message
    try:
        message = come_on(cropped_image_path)
        if message != "Not Encrypt!":
            print(f"Message extracted from {cropped_image_path}: {message}")
        else:
            # 删除不加密的图片
            os.remove(cropped_image_path)
            pass
    except Exception as e:
        print(f"Failed to extract message from {cropped_image_path}: {e}")
        # 删除无法提取信息的图片
        os.remove(cropped_image_path)


if __name__ == '__main__':
    test_pic = os.path.join(UPLOAD_FOLDER, 'output_1688008642.bmp')
    try_to_extract_message(test_pic)
    test_crop_resilience(test_pic, 'x', 3)
    test_crop_resilience(test_pic, 'y', 3)
    test_crop_resilience(test_pic, 'xy', 3)


