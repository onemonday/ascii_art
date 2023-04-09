import unittest
from unittest.mock import Mock
import PIL
import ascii
from PIL import Image


class MyTestCase(unittest.TestCase):
    def test_parse_arguments(self):
        args = ["pic.png", "-od", r"C:\test", "-w", "500"]
        args_parsed = ascii.parse_arguments(args)
        self.assertEqual("pic.png", args_parsed.image)
        self.assertEqual(r"C:\test", args_parsed.output_dir)
        self.assertEqual(500, args_parsed.width)

    def test_random_pic_argument(self):
        args = ["qwerty"]
        self.assertEqual(ascii.initial_checkup(ascii.parse_arguments(args)),
                         "ERROR: picture not found or path to the picture is incorrect.")

    def test_random_pic_extension(self):
        args = ["qwerty.qwerty"]
        self.assertEqual(ascii.initial_checkup(ascii.parse_arguments(args)),
                         "ERROR: picture not found or path to the picture is incorrect.")

    def test_unidentified_image_error(self):
        args = ["qwerty.qwerty"]
        Image.open = Mock(side_effect=PIL.UnidentifiedImageError)
        self.assertEqual("ERROR: picture file is unsupported or corrupted.",
                         ascii.initial_checkup(ascii.parse_arguments(args)))

    def test_image_resize(self):
        image = Image.new("RGB", (1280, 720), "red")
        self.assertEqual((400, 225), ascii.resize_image(image, new_width=400).size)

    def test_conversion_to_ascii(self):
        pixel1 = (0, 0, 0)
        pixel2 = (255, 255, 255)
        pixel3 = (45, 23, 124)
        self.assertEqual(' ', ascii.map_pixel_to_ascii(pixel1))
        self.assertEqual('$', ascii.map_pixel_to_ascii(pixel2))
        self.assertEqual(':', ascii.map_pixel_to_ascii(pixel3))

    def test_constructing_output_filename_with_user_input(self):
        args = ["pic.png", "-od", r"C:\test"]
        args_parsed = ascii.parse_arguments(args)
        self.assertEqual(r"C:\test\ascii.txt",
                         ascii.construct_output_filename(args_parsed))

    def test_constructing_output_filename_without_user_input(self):
        args = [r"C:\test\pic.png"]
        args_parsed = ascii.parse_arguments(args)
        print(type(args_parsed))
        self.assertEqual(r"C:\test\ascii.txt",
                         ascii.construct_output_filename(args_parsed))

    def test_drawing_ascii_txt(self):
        image = Image.new("RGB", (600, 600), "red")
        args = ["test_pic.png"]
        ascii.write_to_file = Mock(return_value="Success!")

        self.assertEqual("Success!",
                         ascii.convert_image_to_ascii(image, ascii.parse_arguments(args)))


if __name__ == '__main__':
    unittest.main()
