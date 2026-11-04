import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab, serial  # noqa: E402
import microbit  # noqa: E402


class ButtonsLab(unittest.TestCase):
    def setUp(self):
        self.lab = load_lab(HERE)

    def test_three_presses_between_iterations_all_count(self):
        microbit.button_a.click(times=3)
        with serial() as out:
            count = self.lab.step(0)
        self.assertEqual(count, 3)
        self.assertEqual(out.getvalue(), "count 3\n")
        self.assertEqual(microbit.display.last_text, "3")

    def test_no_press_no_output(self):
        with serial() as out:
            self.assertEqual(self.lab.step(4), 4)
        self.assertEqual(out.getvalue(), "")

    def test_b_resets(self):
        microbit.button_b.click()
        with serial() as out:
            self.assertEqual(self.lab.step(7), 0)
        self.assertEqual(out.getvalue(), "count 0\n")

    def test_was_pressed_is_consumed(self):
        microbit.button_b.click()
        with serial():
            self.lab.step(5)
            self.assertEqual(self.lab.step(2), 2)   # flag already cleared

    def test_both_held(self):
        microbit.button_a.press()
        microbit.button_b.press()
        with serial() as out:
            self.lab.step(0)
        # A's press counted, then B reset to 0 -> no change printed; held both.
        self.assertEqual(out.getvalue(), "both held\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
