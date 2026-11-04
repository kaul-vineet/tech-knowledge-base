"""Build task check (lab 09): with USE_POT the duty follows pin0.read_analog().

Runs solution.py. To check YOUR version: BUILD_FILE=main.py python -m unittest test_build_task
(Windows PowerShell: $env:BUILD_FILE="main.py"; py -m unittest test_build_task)
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab, serial  # noqa: E402
import microbit  # noqa: E402

BUILD_FILE = os.environ.get("BUILD_FILE", "solution.py")


class PotBuildTask(unittest.TestCase):
    def setUp(self):
        self.lab = load_lab(HERE, BUILD_FILE)
        self.state = self.lab.new_state()
        self.state["on"] = True

    def test_duty_follows_pot(self):
        self.assertTrue(self.lab.USE_POT)
        for value in (0, 300, 1023):
            microbit.pin0.inject_analog(value)
            with serial():
                self.assertEqual(self.lab.step(self.state), value)
            self.assertEqual(microbit.pin2.duty, value)
        self.assertEqual(microbit.pin0.get_mode(), "analog")

    def test_off_means_zero(self):
        self.state["on"] = False
        microbit.pin0.inject_analog(800)
        with serial():
            self.assertEqual(self.lab.step(self.state), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
