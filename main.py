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


def convert_image_to_ascii(image, args):
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
        file = open(args[2], 'w', encoding='utf8', errors='ignore')
        file.write(ascii_art_image)
        file.close()
        return "Success!"
    except FileNotFoundError:
        return "ERROR: output file directory is incorrect"

def initial_checkup(args):
    try:
        image_path = args[1]

        if image_path == "--help" or image_path == "-h":
            return("This program converts your picture to ASCII-art .txt file."
                  "\n\n"
                  "Arguments:\n\n"
                  "Argument 1:"
                  "--help, -h: help page\n"
                  "{$pic_path}: path to the picture\n\n"
                  "Argument 2:\n"
                  "{$txt_path}: path to the output in .txt extension")

        # existence check
        regex = re.compile(r'.*\.txt\Z')
        if regex.search(args[2]) is None:
            return "ERROR: output file is not in .txt extension"

    except IndexError:
        return "ERROR: path not assigned. Please type path to the picture and txt in argv"

    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        return "ERROR: picture not found or path to the picture is incorrect."
    except PIL.UnidentifiedImageError:
        return "ERROR: picture file is unsupported or corrupted."

    return convert_image_to_ascii(image, args)

if __name__ == "__main__":
    print(initial_checkup(args=sys.argv))