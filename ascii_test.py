import runpy
import unittest
import sys
from typing import IO
from unittest.mock import Mock, MagicMock

# import mock as mock

import main
from PIL import Image


class MyTestCase(unittest.TestCase):
    def test_no_arguments(self):
        args = ["main.py"]
        self.assertEqual(main.initial_checkup(args),
                         "ERROR: path not assigned. Please type path to the picture and txt in argv")

    def test_help_1(self):
        args = ["main.py", "--help"]
        self.assertEqual(main.initial_checkup(args), ("This program converts your picture to ASCII-art .txt file."
                                                      "\n\n"
                                                      "Arguments:\n\n"
                                                      "Argument 1:"
                                                      "--help, -h: help page\n"
                                                      "{$pic_path}: path to the picture\n\n"
                                                      "Argument 2:\n"
                                                      "{$txt_path}: path to the output in .txt extension"))

    def test_help_2(self):
        args = ["main.py", "-h"]
        self.assertEqual(main.initial_checkup(args), ("This program converts your picture to ASCII-art .txt file."
                                                      "\n\n"
                                                      "Arguments:\n\n"
                                                      "Argument 1:"
                                                      "--help, -h: help page\n"
                                                      "{$pic_path}: path to the picture\n\n"
                                                      "Argument 2:\n"
                                                      "{$txt_path}: path to the output in .txt extension"))

    def test_output_not_txt(self):
        args = ["main.py", "pic.jpg", "test.png"]
        self.assertEqual(main.initial_checkup(args),
                         "ERROR: output file is not in .txt extension")

    def test_random_pic_argument(self):
        args = ["main.py", "qwerty", "qwerty.txt"]
        self.assertEqual(main.initial_checkup(args),
                         "ERROR: picture not found or path to the picture is incorrect.")

    def test_random_pic_extension(self):
        args = ["main.py", "qwerty.qwerty", "qwerty.txt"]
        self.assertEqual(main.initial_checkup(args),
                         "ERROR: picture not found or path to the picture is incorrect.")

    def test_image_resize(self):
        image = Image.new("RGB", (1280, 720), "red")
        main.resize_image(image)
        self.assertEqual((400, 225), main.resize_image(image).size)

    def test_conversion_to_ascii(self):
        pixel1 = (0, 0, 0)
        pixel2 = (255, 255, 255)
        pixel3 = (45, 23, 124)
        self.assertEqual(' ', main.map_pixel_to_ascii(pixel1))
        self.assertEqual('@', main.map_pixel_to_ascii(pixel2))
        self.assertEqual('"', main.map_pixel_to_ascii(pixel3))

    # def test_drawing_ascii_txt(self):
    #     image = Image.new("RGB", (600, 600), "red")
    #     args = ["main.py", "test_pic.png", "test_output.txt"]
    #
    #     # надо спросить про то, как сделать Mock работы с файлом
    #     open = Mock(return_value=None)
    #     IO.write = Mock(return_value=None)
    #     IO.close = Mock(return_value=None)
    #
    #     self.assertEqual("Success!", main.convert_image_to_ascii(image, args))


if __name__ == '__main__':
    unittest.main()
