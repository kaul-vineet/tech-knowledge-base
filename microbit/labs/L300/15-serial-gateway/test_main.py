import binascii
import io
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab, serial  # noqa: E402
import gateway  # noqa: E402
import serial_link  # noqa: E402


class Device(unittest.TestCase):
    def test_frame_format(self):
        lab = load_lab(HERE)
        self.assertEqual(lab.frame("1,20,100"), "$0081,20,100*1DA1")
        self.assertEqual(lab.crc16("1,20,100"), binascii.crc_hqx(b"1,20,100", 0xFFFF))
        self.assertEqual(lab.crc16("123456789"), 0x29B1)    # CRC-16/CCITT-FALSE check value

    def test_step_prints_one_frame(self):
        lab = load_lab(HERE)
        with serial() as out:
            lab.step(lab.new_state())
        self.assertEqual(out.getvalue(), "$0081,20,127*0B24\n")


class NaiveGatewayHappyPath(unittest.TestCase):
    def test_clean_transcript_is_forwarded(self):
        lines = serial_link.device_bytes(200).decode("ascii").splitlines(keepends=True)
        pub = gateway.run(lines, gateway.JsonLinesPublisher(io.StringIO()))
        self.assertEqual(len(pub.sent), 200)
        self.assertEqual(pub.sent[0], {"topic": "microbit/mb1/telemetry", "qos": 1,
                                       "payload": {"seq": 1, "temp": 20, "light": 100}})
        first = json.loads(pub.out.getvalue().splitlines()[0])
        self.assertEqual(first["payload"]["seq"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
