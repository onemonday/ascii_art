import os.path
import argparse
import sys
import logging

import PIL
from PIL import Image

from modes import Modes
from image import convert_image_to_ascii
from video import convert_video_to_ascii


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
    parser.add_argument("-m", "--mode", type=str, required=True, help="program mode: colored (c), monochrome (bw) or "
                                                                      "video (v)",
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
        if convert_video_to_ascii(args):
            logging.info("video has converted to ASCII-art")
        return

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
