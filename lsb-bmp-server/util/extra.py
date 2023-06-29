from PIL import Image
from util.lsb import come_on
import os

now_dir = os.path.realpath(__file__)
uploads_dir = os.path.dirname(os.path.dirname(now_dir))
UPLOAD_FOLDER = os.path.join(uploads_dir, 'uploads')


def test_crop_resilience(image_path, direction, pixel_count, step):
    """
    Crop an image in all possible ways along both x and y directions and check if the message can still be extracted.

    Args:
        image_path (str): The path of the image to crop.
        direction (str): The direction to crop ('x', 'y', 'xy').
        pixel_count (int): The number of pixels to crop.
        step (int): The step size for the cropping area.
    """
    # Load the image
    image = Image.open(image_path)
    width, height = image.size

    # Determine the direction to crop
    if direction.lower() in ['x', 'xy']:
        start_x = 0
        end_x = width - pixel_count
    if direction.lower() in ['y', 'xy']:
        start_y = 0
        end_y = height - pixel_count

    # Crop the image in all possible ways and test if the message can still be extracted
    if direction.lower() in ['x', 'xy']:
        for i in range(start_x, end_x, step):
            cropped_image_path = image_path[:-4] + f"_cropped_x_{i}_{i + pixel_count}.bmp"
            crop_image(image_path, cropped_image_path, i, 0, pixel_count, height)
            try_to_extract_message(cropped_image_path)

    if direction.lower() in ['y', 'xy']:
        for i in range(start_y, end_y, step):
            cropped_image_path = image_path[:-4] + f"_cropped_y_{i}_{i + pixel_count}.bmp"
            crop_image(image_path, cropped_image_path, 0, i, width, pixel_count)
            try_to_extract_message(cropped_image_path)

    if direction.lower() == 'xy':
        for i in range(start_x, end_x, step):
            for j in range(start_y, end_y, step):
                cropped_image_path = image_path[:-4] + f"_cropped_xy_{i}_{i + pixel_count}_{j}_{j + pixel_count}.bmp"
                crop_image(image_path, cropped_image_path, i, j, pixel_count, pixel_count)
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
        print(f"Message extracted from {cropped_image_path}: {message}")
    except Exception as e:
        print(f"Failed to extract message from {cropped_image_path}: {e}")


if __name__ == '__main__':
    test_pic = os.path.join(UPLOAD_FOLDER, '4X4_lsb_embed.bmp')
    try_to_extract_message(test_pic)
    test_crop_resilience(test_pic, 'x', 1, 1)
    test_crop_resilience(test_pic, 'y', 1, 1)
    test_crop_resilience(test_pic, 'xy', 1, 1)

