"""Build task check (lab 15): framing + CRC + resync; the gateway never crashes on input.

Runs solution.py. To check YOUR version: BUILD_FILE=gateway.py python -m unittest test_build_task
(Windows PowerShell: $env:BUILD_FILE="gateway.py"; py -m unittest test_build_task)
gateway.py as shipped FAILS this check: that is the failureLab "before".
"""
import importlib.util
import io
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import serial_link  # noqa: E402
from gateway import JsonLinesPublisher  # noqa: E402

BUILD_FILE = os.environ.get("BUILD_FILE", "solution.py")


def load():
    spec = importlib.util.spec_from_file_location("gw_under_test", os.path.join(HERE, BUILD_FILE))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def truth(n=200):
    """seq -> (temp, light) exactly as the stub device produced them."""
    return dict((i + 1, (20 + i // 50, 100 + i % 10)) for i in range(n))


class Hardened(unittest.TestCase):
    def setUp(self):
        self.gw = load()
        self.chunks, _ = serial_link.noisy(serial_link.device_bytes(), **serial_link.FAULTS)

    def publish(self, chunks):
        pub = JsonLinesPublisher(io.StringIO())
        if not hasattr(self.gw, "Framer"):           # the naive gateway reads text lines
            chunks = serial_link.as_text_lines(chunks)
        self.gw.run(chunks, pub)
        return pub

    def test_noisy_link_no_crash_no_wrong_value(self):
        pub = self.publish(self.chunks)
        readings = [m["payload"] for m in pub.sent if m["topic"].endswith("/telemetry")]
        self.assertEqual(len(readings), 190)
        t = truth()
        for r in readings:                                   # every forwarded value is real
            self.assertEqual((r["temp"], r["light"]), t[r["seq"]], r)

    def test_metrics_line_explains_the_losses(self):
        pub = self.publish(self.chunks)
        last = pub.sent[-1]
        self.assertEqual(last["topic"], "microbit/gateway/metrics")
        self.assertEqual(last["payload"], {"frames_ok": 190, "bad_len": 6, "bad_crc": 3,
                                           "bad_payload": 0, "resyncs": 9, "skipped_bytes": 184})
        json.loads(pub.out.getvalue().splitlines()[-1])

    def test_chunk_size_does_not_matter(self):
        one_byte = [bytes([b]) for b in b"".join(self.chunks)]
        self.assertEqual(self.publish(one_byte).sent, self.publish(self.chunks).sent)

    def test_garbage_only_input_is_survived(self):
        pub = self.publish([b"\x00\xff$$$999*\r\n$12", b"x*ZZZZ\n$"])
        self.assertEqual([m["topic"] for m in pub.sent], ["microbit/gateway/metrics"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
