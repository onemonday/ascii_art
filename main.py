import sys

import PIL
from PIL import Image
import re

ASCII_CHARS = ' .",:;!~+-xmo*#W&8@'


def resize_image(image, new_width=400):
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)
    return image.resize((new_width, new_height))


def get_pixel_brightness(pixel):
    r, g, b = pixel
    return int((0.2126 * r) + (0.7152 * g) + (0.0722 * b))


def map_pixel_to_ascii(pixel):
    grayscale_value = get_pixel_brightness(pixel)
    num_chars = len(ASCII_CHARS)
    interval_size = 256 / num_chars
    return ASCII_CHARS[int(grayscale_value / interval_size)]


def convert_image_to_ascii(image):
    image = resize_image(image)

    pixels = list(image.getdata())
    ascii_characters = [map_pixel_to_ascii(pixel) for pixel in pixels]

    width, height = image.size
    ascii_characters = ''.join(ascii_characters)

    ascii_art_image = ''
    for i in range(0, len(ascii_characters), width):
        line_end = i + width
        ascii_art_image += ascii_characters[i:line_end] + '\n'

    try:
        file = open(sys.argv[2], 'w', encoding='utf8', errors='ignore')
        print(type(file))
        file.write(ascii_art_image)
        file.close()
    except FileNotFoundError:
        print("ERROR: output file directory is incorrect")
        sys.exit(1)


if __name__ == "__main__":
    try:
        image_path = sys.argv[1]

        if image_path == "--help" or image_path == "-h":
            print("This program converts your picture to ASCII-art .txt file."
                  "\n\n"
                  "Arguments:\n\n"
                  "Argument 1:"
                  "--help, -h: help page\n"
                  "{$pic_path}: path to the picture\n\n"
                  "Argument 2:\n"
                  "{$txt_path}: path to the output in .txt extension")
            sys.exit(0)

        # existence check
        regex = re.compile(r'.*\.txt\Z')
        if regex.search(sys.argv[2]) is not None:
            print("ERROR: output file is not in .txt extension")
            sys.exit(2)

    except IndexError:
        print("ERROR: path not assigned. Please type path to the picture and txt in argv")
        sys.exit(1)

    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        print("ERROR: picture not found or path to the picture is incorrect.")
        sys.exit(1)
    except PIL.UnidentifiedImageError:
        print("ERROR: picture file is unsupported or corrupted.")
        sys.exit(2)

    convert_image_to_ascii(image)