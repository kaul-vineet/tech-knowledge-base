"""Build task check (lab 10): set_high_limit() writes T_HIGH (pointer 0x03) and reads it back.

Runs solution.py. To check YOUR version: BUILD_FILE=main.py python -m unittest test_build_task
(Windows PowerShell: $env:BUILD_FILE="main.py"; py -m unittest test_build_task)
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab  # noqa: E402
from i2c_devices import TMP102  # noqa: E402  (SIMULATED device, stub only)
import microbit  # noqa: E402

BUILD_FILE = os.environ.get("BUILD_FILE", "solution.py")


class THighBuildTask(unittest.TestCase):
    def setUp(self):
        self.lab = load_lab(HERE, BUILD_FILE)
        self.sensor = TMP102()
        microbit.i2c._attach(0x48, self.sensor)

    def test_encode_matches_datasheet(self):
        self.assertEqual(self.lab.encode_temp(80), (0x50, 0x00))     # power-up T_HIGH
        self.assertEqual(self.lab.encode_temp(-25), (0xE7, 0x00))

    def test_write_and_read_back(self):
        self.assertEqual(self.lab.set_high_limit(30.5), 30.5)
        self.assertEqual(microbit.i2c.transactions[0], ("write", 0x48, b"\x03\x1e\x80"))
        self.assertEqual(self.sensor.regs[TMP102.REG_THIGH], 0x1E80)

    def test_negative_limit(self):
        self.assertEqual(self.lab.set_high_limit(-5), -5.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
