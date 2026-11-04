import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab, serial  # noqa: E402
import microbit  # noqa: E402


class LedDisplayLab(unittest.TestCase):
    def setUp(self):
        self.lab = load_lab(HERE)

    def test_intro_sequence(self):
        with serial() as out:
            self.lab.intro()
        kinds = [(k, v) for k, v in microbit.display.history]
        self.assertEqual(kinds[0], ("scroll", "Hi"))
        self.assertEqual(kinds[1], ("show", microbit.Image.HEART))
        self.assertEqual(microbit.display.current_image(), self.lab.DIAMOND)
        self.assertIn("intro done", out.getvalue())

    def test_custom_image_pixels(self):
        d = self.lab.DIAMOND
        self.assertEqual((d.width(), d.height()), (5, 5))
        self.assertEqual(d.get_pixel(2, 0), 9)   # top tip
        self.assertEqual(d.get_pixel(2, 2), 1)   # dim centre
        self.assertEqual(d.get_pixel(0, 0), 0)   # corner off

    def test_step_shows_level_and_wraps(self):
        with serial() as out:
            nxt = self.lab.step(5)
        self.assertEqual(nxt, 6)
        self.assertEqual(microbit.display.get_pixel(4, 4), 5)
        self.assertEqual(out.getvalue(), "brightness 5\n")
        with serial():
            self.assertEqual(self.lab.step(9), 0)

    def test_builtin_images_are_read_only(self):
        with self.assertRaises(TypeError):
            microbit.Image.HEART.set_pixel(0, 0, 9)


if __name__ == "__main__":
    unittest.main(verbosity=2)
