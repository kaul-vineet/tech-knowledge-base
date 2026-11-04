import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab, serial  # noqa: E402
import microbit  # noqa: E402


class TempLightLab(unittest.TestCase):
    def setUp(self):
        self.lab = load_lab(HERE)

    def test_classify_thresholds(self):
        c = self.lab.classify
        self.assertEqual(c(20, 200), "ok")
        self.assertEqual(c(26, 200), "hot")      # threshold is inclusive
        self.assertEqual(c(30, 39), "dark")      # dark wins over hot
        self.assertEqual(c(20, 40), "ok")

    def test_step_normal(self):
        microbit._inject_temperature(21)
        microbit.display.inject_light_level(128)
        with serial() as out:
            self.lab.step()
        self.assertEqual(out.getvalue(), "temp=21,light=128,state=ok\n")
        self.assertEqual(microbit.display.current_image(), microbit.Image.HAPPY)

    def test_step_hot(self):
        microbit._inject_temperature(30)
        microbit.display.inject_light_level(200)
        with serial() as out:
            self.lab.step()
        self.assertEqual(out.getvalue(), "temp=30,light=200,state=hot\n")
        self.assertEqual(microbit.display.last_text, "H")

    def test_step_dark(self):
        microbit.display.inject_light_level(10)
        with serial() as out:
            self.assertEqual(self.lab.step(), "dark")
        self.assertIn("state=dark", out.getvalue())
        self.assertEqual(microbit.display.current_image(), microbit.Image.ASLEEP)


if __name__ == "__main__":
    unittest.main(verbosity=2)
