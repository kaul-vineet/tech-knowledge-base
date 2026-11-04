"""failureLab symptom (observed, seeded): the naive gateway on a noisy serial link."""
import io
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gateway  # noqa: E402
import serial_link  # noqa: E402


class Symptom(unittest.TestCase):
    def test_boot_garbage_crashes_it(self):
        chunks, stats = serial_link.noisy(serial_link.device_bytes(), **serial_link.FAULTS)
        self.assertEqual(stats, {"dropped": 3, "flipped": 5, "cut": 2})
        pub = gateway.JsonLinesPublisher(io.StringIO())
        with self.assertRaises(ValueError):          # dies on line 1, forwards nothing
            gateway.run(serial_link.as_text_lines(chunks), pub)
        self.assertEqual(pub.sent, [])

    def test_a_flipped_digit_is_forwarded_as_truth(self):
        good = "$0081,20,100*1DA1\r\n"
        bad = good.replace("1,20", "1,22")            # one bit: '0' (0x30) -> '2' (0x32)
        pub = gateway.run([bad], gateway.JsonLinesPublisher(io.StringIO()))
        self.assertEqual(pub.sent[0]["payload"]["temp"], 22)   # wrong value, no warning


if __name__ == "__main__":
    unittest.main(verbosity=2)
