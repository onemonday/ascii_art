import argparse
import logging
import os
import sys

import PIL
from PIL import Image, ImageFont, ImageDraw

from modes import Modes

RED_COEFF = 0.2126
GREEN_COEFF = 0.7152
BLUE_COEFF = 0.0722
JPG_CHAR_SAFE_BOX_WIDTH = 4
JPG_CHAR_SAFE_BOX_HEIGHT = 4
FONT = "Anonymous_Pro.ttf"
ASCII_CHARS = r"`.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@"


def construct_output_filename(args: argparse) -> str:
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
    if args.mode == Modes.BW.value:
        output_file += os.sep + "ascii.txt"
    elif args.mode == Modes.COLOR.value:
        output_file += os.sep + "ascii.png"
    return output_file


def write_to_file(output_filename: str, ascii_art_image: str, args: argparse):
    """
    Writes ASCII-art string to file

    :param args: parsed arguments via argparse
    :param output_filename: path to the output file
    :param ascii_art_image: string representation of
                            image (look convert_image_to_ascii)
    :return: string declaring program status
    """
    if args.mode == Modes.BW.value:
        try:
            with open(output_filename, 'w', encoding='utf8', errors='ignore') as file:
                file.write(ascii_art_image)
                logging.info("image has converted to ASCII-art")
        except FileNotFoundError:
            logging.error("output file directory is incorrect")
            sys.exit(3)
        except Exception:
            logging.error("unexpected error occurred while writing to file")
            sys.exit(4)
    elif args.mode == Modes.COLOR.value:
        try:
            ascii_art_image.save(construct_output_filename(args))
            logging.info("image has converted to ASCII-art")
        except FileNotFoundError:
            logging.error("output file directory is incorrect")
            sys.exit(3)
        except Exception:
            logging.error("unexpected error occurred while writing to file")
            sys.exit(4)


def resize_image(image: Image, new_width: int, is_video: bool = False) -> PIL.Image:
    """
    Resizes the image depending on selected width

    :param is_video: bool variable that indicates whether the image is a frame from a video
    :param image: PIL Image object
    :param new_width: positive integer with new width
    :return: resized PIL Image object
    """
    new_height = None

    if new_width is None:
        if not is_video:
            logging.info("custom width was not defined. " +
                         "ASCII-art will be the same size as the picture")
        new_height = image.size[1]
        new_width = image.size[0]
    elif new_width == 0:
        if not is_video:
            logging.warning("user has entered zero width. " +
                            "ASCII-art will be the same size as the picture")
        new_height = image.size[1]
        new_width = image.size[0]
    elif new_width < 0:
        if not is_video:
            logging.warning("user has entered width below zero. " +
                            "ASCII-art will be the same size as the picture")
        new_height = image.size[1]
        new_width = image.size[0]
    elif new_width > 0:
        width, height = image.size
        ratio = height / width
        new_height = int(new_width * ratio)
    else:
        raise NotImplementedError("unexpected error occurred while resizing image")

    return image.resize((new_width, new_height))


def get_pixel_brightness(pixel: tuple) -> int:
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


def convert_image_to_ascii(image: Image, args: argparse, is_video: bool = False):
    """
    Converts image into ASCII-art string which is written to the .txt file

    :param image: PIL Image object
    :param args: parsed console arguments
    :return: string declaring program status
    """
    try:
        image = resize_image(image, args.width, is_video)
    except NotImplementedError:
        logging.error("unexpected error occurred while resizing image")
        sys.exit(3)

    if args.mode == Modes.COLOR.value:
        global ASCII_CHARS
        ASCII_CHARS = ASCII_CHARS[::-1]

    pixels = list(image.convert(mode="RGB").getdata())
    ascii_characters = [map_pixel_to_ascii(pixel) for pixel in pixels]

    width, height = image.size
    ascii_characters = ''.join(ascii_characters)

    ascii_art_image = list()
    for i in range(0, len(ascii_characters), width):
        line_end = i + width
        ascii_art_image.append(ascii_characters[i:line_end])
        ascii_art_image.append('\n')

    ascii_art_image_str = ''.join(ascii_art_image)

    if is_video:
        return draw_colored_image(ascii_art_image_str, pixels, image.size)

    if args.mode == Modes.COLOR.value:
        output_image = draw_colored_image(ascii_art_image_str, pixels, image.size)
        write_to_file(construct_output_filename(args), output_image, args)
    elif args.mode == Modes.BW.value:
        write_to_file(construct_output_filename(args), ascii_art_image_str)


def draw_colored_image(ascii_art_string: str, pixels: list, size: tuple) -> PIL.Image:
    """
        Draws ASCII-art strinng into the PIL image and saves it

        :param ascii_art_string: string representation of
                                 image (look convert_image_to_ascii)
        :param pixels: list of RGB-tuples representing an image
        :param size: image size
        :param output_file: output filename
        """
    width, height = size[0] * JPG_CHAR_SAFE_BOX_WIDTH, size[1] * JPG_CHAR_SAFE_BOX_HEIGHT

    output_image = Image.new(mode="RGB", size=(width, height), color="black")
    font = ImageFont.truetype(FONT)
    draw = ImageDraw.Draw(output_image)

    x, y = 0, 0
    char_index = 0
    for char in ascii_art_string:
        if char == '\n':
            y += JPG_CHAR_SAFE_BOX_HEIGHT
            x = 0
            continue

        draw.text((x, y), text=char, fill=pixels[char_index], font=font)
        x += JPG_CHAR_SAFE_BOX_WIDTH
        char_index += 1

    return output_image
