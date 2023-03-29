import runpy
import unittest
import sys

import main


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


if __name__ == '__main__':
    unittest.main()
