import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab, serial  # noqa: E402
from i2c_devices import TMP102  # noqa: E402  (SIMULATED device, stub only)
import microbit  # noqa: E402


class I2CSensorLab(unittest.TestCase):
    def setUp(self):
        self.lab = load_lab(HERE)
        self.sensor = TMP102(celsius=21.5)
        microbit.i2c._attach(0x48, self.sensor)

    def test_decode_datasheet_examples(self):
        d = self.lab.decode_temp
        # TI TMP102 table 6-2: 50 C = 0x320, 25 C = 0x190, -0.25 C = 0xFFC, -25 C = 0xE70
        self.assertEqual(d(0x32, 0x00), 50.0)
        self.assertEqual(d(0x19, 0x00), 25.0)
        self.assertEqual(d(0xFF, 0xC0), -0.25)
        self.assertEqual(d(0xE7, 0x00), -25.0)

    def test_step_reads_pointer_then_two_bytes(self):
        with serial() as out:
            self.assertEqual(self.lab.step(), 21.5)
        self.assertEqual(out.getvalue(), "temp_c=21.50\n")
        self.assertEqual(microbit.i2c.transactions,
                         [("write", 0x48, b"\x00"), ("read", 0x48, b"\x15\x80")])

    def test_config_register_power_up_value(self):
        self.assertEqual(self.lab.read_register(self.lab.REG_CONFIG), b"\x60\xa0")

    def test_negative_temperature(self):
        self.sensor.set_temperature(-10.25)
        with serial() as out:
            self.lab.step()
        self.assertEqual(out.getvalue(), "temp_c=-10.25\n")

    def test_missing_device_is_reported_not_crashing(self):
        microbit.i2c._detach(0x48)
        with serial() as out:
            self.assertIsNone(self.lab.step())
        self.assertEqual(out.getvalue(), "i2c: no device at 0x48 (errno 19)\n")
        self.assertEqual(microbit.display.current_image(), microbit.Image.NO)

    def test_scan_lists_attached_addresses(self):
        self.assertEqual(microbit.i2c.scan(), [0x48])


if __name__ == "__main__":
    unittest.main(verbosity=2)
