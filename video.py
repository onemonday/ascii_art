import argparse
import logging
import os

import cv2
import numpy as np
from PIL import Image

from image import JPG_CHAR_SAFE_BOX_HEIGHT, JPG_CHAR_SAFE_BOX_WIDTH, convert_image_to_ascii


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
    output_file += os.sep + "ascii.avi"
    return output_file


def resize_video(width: int, height: int, new_width: int) -> tuple[int, int]:
    """
    Resizes the video depending on selected width

    :param width: width of the video
    :param height: height of the video
    :param new_width: new width of the video
    :return: tuple with new width and height
    """
    if new_width is None:
        logging.info("custom width was not defined. " +
                     "ASCII-art will be the same size as the video")
        result_height = height * JPG_CHAR_SAFE_BOX_HEIGHT
        result_width = width * JPG_CHAR_SAFE_BOX_WIDTH
    elif new_width == 0:
        logging.info("user has entered zero width. " +
                     "ASCII-art will be the same size as the video")
        result_height = height * JPG_CHAR_SAFE_BOX_HEIGHT
        result_width = width * JPG_CHAR_SAFE_BOX_WIDTH
    elif new_width < 0:
        logging.warning("user has entered width below zero. " +
                        "ASCII-art will be the same size as the video")
        result_height = height * JPG_CHAR_SAFE_BOX_HEIGHT
        result_width = width * JPG_CHAR_SAFE_BOX_WIDTH
    elif new_width > 0:
        ratio = height / width
        result_height = int(new_width * ratio) * JPG_CHAR_SAFE_BOX_HEIGHT
        result_width = new_width * JPG_CHAR_SAFE_BOX_WIDTH

    return result_width, result_height


def render_ascii_video(video: cv2.VideoCapture, args: argparse):
    fps = video.get(cv2.CAP_PROP_FPS)
    height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    size = resize_video(width, height, args.width)

    output = cv2.VideoWriter(construct_output_filename(args), cv2.VideoWriter_fourcc(*'MJPG'), fps, size)
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


def convert_video_to_ascii(args: argparse) -> bool:
    """
    Converts video into ASCII-art video .avi file
    :param args: parsed console arguments
    """
    if (
        args.image.endswith(".png")
        or args.image.endswith(".jpg")
        or args.image.endswith(".jpeg")
    ):
        logging.error("video file is an image. " +
                        "Use image mode instead (-m bw or -m c)")
        return False


    video = cv2.VideoCapture(args.image)
    if not video.isOpened():
        logging.error("file was not opened: it may not exist or " +
                      "be corrupted")
        return False

    render_ascii_video(video, args)
    return True
