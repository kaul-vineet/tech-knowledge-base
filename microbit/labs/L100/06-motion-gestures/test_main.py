import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab, serial  # noqa: E402
import microbit  # noqa: E402


class MotionLab(unittest.TestCase):
    def setUp(self):
        self.lab = load_lab(HERE)

    def test_tilt_thresholds(self):
        t = self.lab.tilt
        self.assertEqual([t(-800), t(-300), t(0), t(300), t(301)],
                         ["left", "flat", "flat", "flat", "right"])

    def test_flat_face_up(self):
        microbit.accelerometer.inject_axes(0, 0, -1024)
        microbit.accelerometer.inject_gesture("face up")
        with serial() as out:
            self.lab.step()
        self.assertEqual(out.getvalue(),
                         "x=0,y=0,z=-1024,tilt=flat,gesture=face up\n")

    def test_tilt_right_shows_arrow(self):
        microbit.accelerometer.inject_axes(x=800)
        with serial() as out:
            self.assertEqual(self.lab.step(), "right")
        self.assertIn("tilt=right", out.getvalue())
        self.assertEqual(microbit.display.current_image(), microbit.Image.ARROW_E)

    def test_shake_reported_once(self):
        microbit.accelerometer.inject_gesture("shake")
        with serial() as out:
            self.lab.step()
            self.lab.step()
        self.assertEqual(out.getvalue().count("shake!"), 1)
        self.assertIn(("show", microbit.Image.SURPRISED), microbit.display.history)


if __name__ == "__main__":
    unittest.main(verbosity=2)
