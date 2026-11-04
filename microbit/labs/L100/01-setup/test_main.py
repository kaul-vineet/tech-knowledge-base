import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab, serial  # noqa: E402
import microbit  # noqa: E402


class SetupLab(unittest.TestCase):
    def setUp(self):
        self.lab = load_lab(HERE)

    def test_hello_shows_image_and_prints(self):
        with serial() as out:
            self.lab.hello()
        self.assertEqual(out.getvalue(), "hello from micro:bit\n")
        self.assertEqual(microbit.display.current_image(), microbit.Image.HAPPY)

    def test_step_counts_up(self):
        with serial() as out:
            n = self.lab.step(0)
            n = self.lab.step(n)
        self.assertEqual(n, 2)
        self.assertEqual(out.getvalue(), "tick 1\ntick 2\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
