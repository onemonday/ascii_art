import enum
import os.path
import argparse
import sys
import logging

import PIL
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import cv2


RED_COEFF = 0.2126
GREEN_COEFF = 0.7152
BLUE_COEFF = 0.0722

JPG_CHAR_SAFE_BOX_WIDTH = 4
JPG_CHAR_SAFE_BOX_HEIGHT = 4

FONT = "Anonymous_Pro.ttf"
ASCII_CHARS = r"`.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@"


class Modes(enum.Enum):
    """
    Enum class for modes
    """
    BW = "bw"
    COLOR = "c"
    VIDEO = "v"


def resize_image(image: Image, new_width: int) -> PIL.Image:
    """
    Resizes the image depending on selected width

    :param image: PIL Image object
    :param new_width: positive integer with new width
    :return: resized PIL Image object
    """
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)
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
    if args.width is None:
        if not is_video:
            logging.info("custom width was not defined. " +
                         "ASCII-art will be the same size as the picture")
    elif args.width > 0:
        image = resize_image(image, args.width)
    elif args.width < 0 and not is_video:
        logging.warning("user has entered width below zero. " +
                        "ASCII-art will be the same size as the picture")

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
        try:
            output_image.save(construct_output_filename(args))
            logging.info("image has converted to ASCII-art")
        except FileNotFoundError:
            logging.error("output file directory is incorrect")

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


def convert_video_to_ascii(args: argparse):
    """
    Converts video into ASCII-art video .avi file
    :param args: parsed console arguments
    """
    try:
        video = cv2.VideoCapture(args.image)
    except FileNotFoundError:
        logging.error("video file was not found")
        return

    new_height, new_width = None, None
    fps = video.get(cv2.CAP_PROP_FPS)
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))

    if args.width is None:
        logging.info("custom width was not defined. " +
                     "ASCII-art will be the same size as the video")
        new_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)) * JPG_CHAR_SAFE_BOX_HEIGHT
        new_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH)) * JPG_CHAR_SAFE_BOX_WIDTH
    elif args.width < 0:
        logging.warning("user has entered width below zero. " +
                        "ASCII-art will be the same size as the picture")
        new_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)) * JPG_CHAR_SAFE_BOX_HEIGHT
        new_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH)) * JPG_CHAR_SAFE_BOX_WIDTH
    elif args.width > 0:
        ratio = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)) / int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        new_height = int(args.width * ratio) * JPG_CHAR_SAFE_BOX_HEIGHT
        new_width = args.width * JPG_CHAR_SAFE_BOX_WIDTH

    output = cv2.VideoWriter(construct_output_filename(args), cv2.VideoWriter_fourcc(*'MJPG'), fps, (new_width, new_height))
    while True:
        ret, image = video.read()
        if ret is True:
            image = Image.fromarray(image)
            ascii_image = convert_image_to_ascii(image, args, is_video=True)

            output.write(np.array(ascii_image))
            cv2.imshow('ASCII-art', np.array(ascii_image))
            key = cv2.waitKey(1)
            if key == ord("q"):
                break
        else:
            break
    video.release()
    output.release()
    cv2.destroyAllWindows()


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
    elif args.mode == Modes.VIDEO.value:
        output_file += os.sep + "ascii.avi"
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
    parser.add_argument("-m", "--mode", type=str, required=True, help="program mode: colored (c), monochrome (bw) or video (v)",
                        choices=("c", "bw", "v"))
    return parser.parse_args(args)


def initial_checkup(args: argparse):
    """
    Initial function: tries to open the image
    and call the convert_image_to_ascii function


    :param args: parsed console arguments
    :return: string declaring program status
    """

    if args.mode == Modes.VIDEO.value:
        return convert_video_to_ascii(args)

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
