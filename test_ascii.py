import unittest
from unittest.mock import Mock
import PIL
import cv2

import ascii
import logging
from PIL import Image

import image
import video


class MyTestCase(unittest.TestCase):
    def test_parse_arguments(self):
        args = ["pic.png", "-od", r"C:\test", "-w", "500", "-m", "bw"]
        args_parsed = ascii.parse_arguments(args)
        self.assertEqual("pic.png", args_parsed.image)
        self.assertEqual(r"C:\test", args_parsed.output_dir)
        self.assertEqual(500, args_parsed.width)

    def test_random_pic_argument(self):
        args = ["qwerty", "-m", "bw"]
        with self.assertLogs('root', level='INFO') as cm:
            ascii.initial_checkup(ascii.parse_arguments(args))
        self.assertEqual(["ERROR:root:picture not found or path to the picture is incorrect"], cm.output)

    def test_random_pic_extension(self):
        args = ["qwerty.qwerty", "-m", "bw"]
        with self.assertLogs('root', level='INFO') as cm:
            ascii.initial_checkup(ascii.parse_arguments(args))
        self.assertEqual(["ERROR:root:picture not found or path to the picture is incorrect"], cm.output)

    def test_unidentified_image_error(self):
        args = ["qwerty.qwerty", "-m", "bw"]
        Image.open = Mock(side_effect=PIL.UnidentifiedImageError)
        with self.assertLogs('root', level='INFO') as cm:
            ascii.initial_checkup(ascii.parse_arguments(args))
        self.assertEqual(["ERROR:root:picture file is unsupported or corrupted"], cm.output)

    def test_conversion_to_ascii(self):
        pixel1 = (0, 0, 0)
        pixel2 = (255, 255, 255)
        pixel3 = (45, 23, 124)
        self.assertEqual('`', image.map_pixel_to_ascii(pixel1))
        self.assertEqual('@', image.map_pixel_to_ascii(pixel2))
        self.assertEqual('+', image.map_pixel_to_ascii(pixel3))

    def test_constructing_txt_output_filename_with_user_input(self):
        args = ["pic.png", "-od", r"C:\test", "-m", "bw"]
        args_parsed = ascii.parse_arguments(args)
        self.assertEqual(r"C:\test\ascii.txt",
                         image.construct_output_filename(args_parsed))

    def test_constructing_txt_output_filename_without_user_input(self):
        args = [r"C:\test\pic.png", "-m", "bw"]
        args_parsed = ascii.parse_arguments(args)
        self.assertEqual(r"C:\test\ascii.txt",
                         image.construct_output_filename(args_parsed))

    def test_constructing_png_output_filename_with_user_input(self):
        args = ["pic.png", "-od", r"C:\test", "-m", "c"]
        args_parsed = ascii.parse_arguments(args)
        self.assertEqual(r"C:\test\ascii.png",
                         image.construct_output_filename(args_parsed))

    def test_constructing_png_output_filename_without_user_input(self):
        args = [r"C:\test\pic.png", "-m", "c"]
        args_parsed = ascii.parse_arguments(args)
        self.assertEqual(r"C:\test\ascii.png",
                         image.construct_output_filename(args_parsed))

    def test_constructing_video_output_filename_with_user_input(self):
        args = ["pic.avi", "-od", r"C:\test", "-m", "v"]
        args_parsed = ascii.parse_arguments(args)
        self.assertEqual(r"C:\test\ascii.avi",
                         video.construct_output_filename(args_parsed))

    def test_constructing_video_output_filename_without_user_input(self):
        args = [r"C:\test\vid.avi", "-m", "v"]
        args_parsed = ascii.parse_arguments(args)
        self.assertEqual(r"C:\test\ascii.avi",
                         video.construct_output_filename(args_parsed))

    def test_drawing_ascii_txt(self):
        test_image = Image.new("RGB", (5, 5), "red")
        args = ["test_pic.png", "-m", "bw"]

        with self.assertLogs('root', level='INFO') as cm:
            image.write_to_file = Mock(side_effect=logging.info("image has converted to ASCII-art"),
                                       return_value=None)
            image.convert_image_to_ascii(test_image, ascii.parse_arguments(args))
        self.assertEqual(["INFO:root:image has converted to ASCII-art",
                          "INFO:root:custom width was not defined. " +
                          "ASCII-art will be the same size as the picture"],
                         cm.output)

    def test_drawing_ascii_png(self):
        test_image = Image.new("RGB", (5, 5), "red")
        args = ["test_pic.png", "-m", "c"]

        with self.assertLogs('root', level='INFO') as cm:
            image.write_to_file = Mock(side_effect=logging.info("image has converted to ASCII-art"),
                                       return_value=None)
            image.convert_image_to_ascii(test_image, ascii.parse_arguments(args))
        self.assertEqual(["INFO:root:image has converted to ASCII-art",
                          "INFO:root:custom width was not defined. " +
                          "ASCII-art will be the same size as the picture"],
                         cm.output)

    def test_resizing_video_set_width(self):
        width, height = 1920, 1080
        new_width, new_height = video.resize_video(width, height, 1280)
        self.assertEqual(1280 * image.JPG_CHAR_SAFE_BOX_WIDTH, new_width)
        self.assertEqual(720 * image.JPG_CHAR_SAFE_BOX_HEIGHT, new_height)

    def test_resizing_video_empty_width(self):
        width, height = 1920, 1080
        with self.assertLogs('root', level='INFO') as cm:
            new_width, new_height = video.resize_video(width, height, None)
        self.assertEqual(["INFO:root:custom width was not defined. " +
                          "ASCII-art will be the same size as the video"],
                         cm.output)
        self.assertEqual(1920 * image.JPG_CHAR_SAFE_BOX_WIDTH, new_width)
        self.assertEqual(1080 * image.JPG_CHAR_SAFE_BOX_HEIGHT, new_height)

    def test_resizing_video_null_width(self):
        width, height = 1920, 1080
        with self.assertLogs('root', level='INFO') as cm:
            new_width, new_height = video.resize_video(width, height, 0)
        self.assertEqual(["INFO:root:user has entered zero width. " +
                          "ASCII-art will be the same size as the video"],
                         cm.output)
        self.assertEqual(1920 * image.JPG_CHAR_SAFE_BOX_WIDTH, new_width)
        self.assertEqual(1080 * image.JPG_CHAR_SAFE_BOX_HEIGHT, new_height)

    def test_resizing_video_negative_width(self):
        width, height = 1920, 1080
        with self.assertLogs('root', level='INFO') as cm:
            new_width, new_height = video.resize_video(width, height, -1)
        self.assertEqual(["WARNING:root:user has entered width below zero. " +
                          "ASCII-art will be the same size as the video"],
                         cm.output)
        self.assertEqual(1920 * image.JPG_CHAR_SAFE_BOX_WIDTH, new_width)
        self.assertEqual(1080 * image.JPG_CHAR_SAFE_BOX_HEIGHT, new_height)

    def test_resizing_image_negative_width(self):
        test_image = Image.new("RGB", (1280, 720), "red")
        with self.assertLogs('root', level='INFO') as cm:
            new_width, new_height = image.resize_image(test_image, -200, False).size
        self.assertEqual(["WARNING:root:user has entered width below zero. " +
                          "ASCII-art will be the same size as the picture"],
                         cm.output)
        self.assertEqual(1280, new_width)
        self.assertEqual(720, new_height)

    def test_resizing_image_empty_width(self):
        test_image = Image.new("RGB", (1280, 720), "red")
        with self.assertLogs('root', level='INFO') as cm:
            new_width, new_height = image.resize_image(test_image, None, False).size
        self.assertEqual(["INFO:root:custom width was not defined. " +
                          "ASCII-art will be the same size as the picture"],
                         cm.output)
        self.assertEqual(1280, new_width)
        self.assertEqual(720, new_height)

    def test_resizing_image_null_width(self):
        test_image = Image.new("RGB", (1280, 720), "red")
        with self.assertLogs('root', level='INFO') as cm:
            new_width, new_height = image.resize_image(test_image, 0, False).size
        self.assertEqual(["WARNING:root:user has entered zero width. " +
                          "ASCII-art will be the same size as the picture"],
                         cm.output)
        self.assertEqual(1280, new_width)
        self.assertEqual(720, new_height)

    def test_resizing_image_normal_behaviour(self):
        test_image = Image.new("RGB", (1280, 720), "red")
        self.assertEqual((400, 225), image.resize_image(test_image, new_width=400).size)

    def test_video_random_input(self):
        args = ["notvideo.qwerty", "-m", "v"]
        args_parsed = ascii.parse_arguments(args)
        cv2.VideoCapture.isOpened = Mock(return_value=False)
        with self.assertLogs('root', level='INFO') as cm:
            video.convert_video_to_ascii(args_parsed)
        self.assertEqual(["ERROR:root:video file is unsupported or corrupted"], cm.output)

    def test_video_normal_behaviour(self):
        args = ["test_video.avi", "-m", "v"]
        args_parsed = ascii.parse_arguments(args)

        cv2.VideoCapture = Mock()
        video.render_ascii_video = Mock()

        with self.assertLogs('root', level='INFO') as cm:
            ascii.initial_checkup(args_parsed)
        self.assertEqual(["INFO:root:video has converted to ASCII-art"], cm.output)

    def test_jpg_instead_of_video(self):
        args = ["pic.jpg", "-m", "v"]
        args_parsed = ascii.parse_arguments(args)

        with self.assertLogs('root', level='INFO') as cm:
            ascii.initial_checkup(args_parsed)
        self.assertEqual(["ERROR:root:video file is an image. " +
                          "Use image mode instead (-m bw or -m c)"], cm.output)

    def test_png_instead_of_video(self):
        args = ["pic.png", "-m", "v"]
        args_parsed = ascii.parse_arguments(args)

        with self.assertLogs('root', level='INFO') as cm:
            ascii.initial_checkup(args_parsed)
        self.assertEqual(["ERROR:root:video file is an image. " +
                          "Use image mode instead (-m bw or -m c)"], cm.output)

    def test_jpeg_instead_of_video(self):
        args = ["pic.jpeg", "-m", "v"]
        args_parsed = ascii.parse_arguments(args)

        with self.assertLogs('root', level='INFO') as cm:
            ascii.initial_checkup(args_parsed)
        self.assertEqual(["ERROR:root:video file is an image. " +
                          "Use image mode instead (-m bw or -m c)"], cm.output)

    def test_gif_instead_of_video(self):
        args = ["pic.gif", "-m", "v"]
        args_parsed = ascii.parse_arguments(args)

        cv2.VideoCapture = Mock()
        video.render_ascii_video = Mock()

        with self.assertLogs('root', level='INFO') as cm:
            ascii.initial_checkup(args_parsed)
        self.assertEqual(["INFO:root:video has converted to ASCII-art"], cm.output)


if __name__ == '__main__':
    unittest.main()
