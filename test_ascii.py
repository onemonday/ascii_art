import unittest
from unittest.mock import Mock
import PIL
import ascii
import logging
from PIL import Image


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

    def test_image_resize(self):
        image = Image.new("RGB", (1280, 720), "red")
        self.assertEqual((400, 225), ascii.resize_image(image, new_width=400).size)

    def test_conversion_to_ascii(self):
        pixel1 = (0, 0, 0)
        pixel2 = (255, 255, 255)
        pixel3 = (45, 23, 124)
        self.assertEqual('$', ascii.map_pixel_to_ascii(pixel1))
        self.assertEqual('\'', ascii.map_pixel_to_ascii(pixel2))
        self.assertEqual('*', ascii.map_pixel_to_ascii(pixel3))

    def test_constructing_output_filename_with_user_input(self):
        args = ["pic.png", "-od", r"C:\test", "-m", "bw"]
        args_parsed = ascii.parse_arguments(args)
        self.assertEqual(r"C:\test\ascii.txt",
                         ascii.construct_output_filename(args_parsed))

    def test_constructing_output_filename_without_user_input(self):
        args = [r"C:\test\pic.png", "-m", "bw"]
        args_parsed = ascii.parse_arguments(args)
        print(type(args_parsed))
        self.assertEqual(r"C:\test\ascii.txt",
                         ascii.construct_output_filename(args_parsed))

    def test_drawing_ascii_txt(self):
        image = Image.new("RGB", (5, 5), "red")
        args = ["test_pic.png", "-m", "bw"]

        with self.assertLogs('root', level='INFO') as cm:
            ascii.write_to_file = Mock(side_effect=logging.info("image has converted to ASCII-art"),
                                       return_value=None)
            ascii.convert_image_to_ascii(image, ascii.parse_arguments(args))
        self.assertEqual(["INFO:root:image has converted to ASCII-art",
                          "INFO:root:custom width was not defined. " +
                          "ASCII-art will be the same size as the picture"],
                         cm.output)


if __name__ == '__main__':
    unittest.main()
