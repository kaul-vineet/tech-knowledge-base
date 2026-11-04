import binascii
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab, serial  # noqa: E402
import link_sim  # noqa: E402
import radio  # noqa: E402


class Frames(unittest.TestCase):
    def setUp(self):
        self.lab = load_lab(HERE)

    def test_crc16_check_value(self):
        # CRC-16/CCITT-FALSE check value from the reveng catalogue: "123456789" -> 0x29B1
        self.assertEqual(self.lab.crc16("123456789"), 0x29B1)
        self.assertEqual(self.lab.crc16("D:7:21"), binascii.crc_hqx(b"D:7:21", 0xFFFF))

    def test_round_trip_and_fits_one_packet(self):
        frame = self.lab.encode("D", 20, "r20")
        self.assertEqual(self.lab.decode(frame), ("D", 20, "r20"))
        self.assertLessEqual(3 + len(frame), 32)          # default radio length

    def test_one_flipped_bit_is_rejected(self):
        frame = self.lab.encode("D", 3, "r3")
        bad = frame.replace("r3", "r2")                    # '3' -> '2' is one bit
        self.assertIsNone(self.lab.decode(bad))
        for junk in ("", "hello", "D:1:x:12", "D:x:1:" + "0000"):
            self.assertIsNone(self.lab.decode(junk))

    def test_bad_frame_counted_not_delivered(self):
        state = self.lab.new_state()
        radio._inject_str("D:1:r1:0000")
        radio._inject(b"\x02raw")
        with serial() as out:
            self.lab.receive(state)
        self.assertEqual(state["stats"], {"tx": 0, "rx": 2, "bad": 2, "delivered": 0})
        self.assertEqual(out.getvalue(), "")

    def test_json_line_parses(self):
        state = self.lab.new_state()
        line = self.lab.jline(1234, state["stats"])
        self.assertEqual(json.loads(line), {"t": 1234, "tx": 0, "rx": 0, "bad": 0, "delivered": 0})


class HappyPath(unittest.TestCase):
    def test_quiet_link_delivers_everything(self):
        res = link_sim.run("main.py")
        self.assertEqual(res["delivered"], ["r%d" % i for i in range(1, 21)])
        self.assertIn("rx 1 r1", res["serial"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
