import os.path
import argparse
import sys
import logging

import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

RED_COEFF = 0.2126
GREEN_COEFF = 0.7152
BLUE_COEFF = 0.0722

JPG_CHAR_SAFE_BOX = 6

ASCII_CHARS = r"'.'`^\",:;Il!i><~+_-?][}{1)(|\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

def resize_image(image: Image, new_width: int):
    """
    Resizes the image depending on selected

    :param image: PIL Image object
    :param new_width: positive integer with new width
    :return: resized PIL Image object
    """
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)
    return image.resize((new_width, new_height))


def get_pixel_brightness(pixel: tuple):
    """
    Calculates the pixel brightness

    :param pixel: RGB-tuple
    :return: integer which represents pixel brightness
    """
    r, g, b = pixel
    # formula of pixel brightness
    return int((RED_COEFF * r) + (GREEN_COEFF * g) + (BLUE_COEFF * b))


def map_pixel_to_ascii(pixel: tuple):
    """
    Matches pixel with ASCII-character depending on it's brightness

    :param pixel: RGB-tuple
    :return: ASCII-character which represents the pixel
    """

    grayscale_value = get_pixel_brightness(pixel)
    num_chars = len(ASCII_CHARS)
    interval_size = 256 / num_chars
    return ASCII_CHARS[int(grayscale_value / interval_size)]


def convert_image_to_ascii(image: Image, args: argparse):
    """
    Converts image into ASCII-art string which is written to the .txt file

    :param image: PIL Image object
    :param args: parsed console arguments
    :return: string declaring program status
    """
    if args.width is None:
        logging.info("custom width was not defined. " +
                     "ASCII-art will be the same size as the picture")
    elif args.width > 0:
        image = resize_image(image, args.width)
    else:
        logging.warning("user has entered width below zero. " +
                        "ASCII-art will be the same size as the picture")

    if args.mode == "c":
        global ASCII_CHARS
        ASCII_CHARS = ASCII_CHARS[::-1]

    pixels = list(image.convert(mode="RGB").getdata())
    ascii_characters = [map_pixel_to_ascii(pixel) for pixel in pixels]

    width, height = image.size
    ascii_characters = ''.join(ascii_characters)

    ascii_art_image = ''
    for i in range(0, len(ascii_characters), width):
        line_end = i + width
        ascii_art_image += ascii_characters[i:line_end] + '\n'

    if args.mode == "c":
        draw_colored_image(ascii_art_image, pixels, image.size, construct_output_filename(args))
    elif args.mode == "bw":
        write_to_file(construct_output_filename(args), ascii_art_image)


def draw_colored_image(ascii_art_string: str, pixels: list, size: tuple, output_file: str):
    """
        Draws ASCII-art strinng into the PIL image and saves it

        :param ascii_art_string: string representation of
                                 image (look convert_image_to_ascii)
        :param pixels: list of RGB-tuples representing an image
        :param size: image size
        :param output_file: output filename
        """
    width, height = size[0] * JPG_CHAR_SAFE_BOX, size[1] * JPG_CHAR_SAFE_BOX

    output_image = Image.new(mode="RGB", size=(width, height), color="white")
    font = ImageFont.truetype("Anonymous_Pro.ttf")
    draw = ImageDraw.Draw(output_image)

    x, y = 0, 0
    char_index = 0
    for char in ascii_art_string:
        if char == '\n':
            y += JPG_CHAR_SAFE_BOX
            x = 0
            continue

        draw.text((x, y), text=char, fill=pixels[char_index], font=font)
        x += JPG_CHAR_SAFE_BOX
        char_index += 1

    try:
        output_image.save(output_file)
        logging.info("image has converted to ASCII-art")
    except FileNotFoundError:
        logging.error("output file directory is incorrect")


def construct_output_filename(args: argparse):
    """
    Constructs output filename depending on user's choice.
    If user typed output directory in -od, output file will be there.
    Otherwise, it will be in the same place as the image

    :param args: parsed console arguments
    :return: string with correct output file path
    """
    output_file = args.output_dir
    if output_file is None:
        output_file = os.path.dirname(args.image)
    if args.mode == "bw":
        output_file += os.sep + "ascii.txt"
    elif args.mode == "c":
        output_file += os.sep + "ascii.png"
    return output_file


def write_to_file(output_filename: str, ascii_art_image: str):
    """
    Writes ASCII-art string to file

    :param output_filename: path to the output file
    :param ascii_art_image: string representation of
                            image (look convert_image_to_ascii)
    :return: string declaring program status
    """
    try:
        with open(output_filename, 'w', encoding='utf8', errors='ignore') as file:
            file.write(ascii_art_image)
            logging.info("image has converted to ASCII-art")
    except FileNotFoundError:
        logging.error("output file directory is incorrect")
        sys.exit(3)


def parse_arguments(args: argparse):
    """
    Parse list of arguments via argparse

    :param args: list of arguments
    :return: parsed arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="path to the image")
    parser.add_argument("-od", "--output_dir", type=str, help="output directory")
    parser.add_argument("-w", "--width", type=int, help="width of ASCII-art file")
    parser.add_argument("-m", "--mode", type=str, required=True, help="program mode: colored (c) or monochrome (bw)",
                        choices=("c", "bw"))
    return parser.parse_args(args)


def initial_checkup(args: argparse):
    """
    Initial function: tries to open the image
    and call the convert_image_to_ascii function


    :param args: parsed console arguments
    :return: string declaring program status
    """
    try:
        image = Image.open(args.image)
    except FileNotFoundError:
        logging.error("picture not found or path to the picture is incorrect")
        return
    except PIL.UnidentifiedImageError:
        logging.error("picture file is unsupported or corrupted")
        return

    return convert_image_to_ascii(image, args)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    initial_checkup(parse_arguments(sys.argv[1:]))
