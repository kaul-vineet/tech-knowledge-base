"""Build task check (lab 07): every received btn/tmp message is acknowledged.

Runs solution.py on two stub boards. To check YOUR version, copy your main.py
to solution.py (or set BUILD_FILE=main.py) and run: python -m unittest test_build_task
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_boards, serial  # noqa: E402

BUILD_FILE = os.environ.get("BUILD_FILE", "solution.py")


class AckBuildTask(unittest.TestCase):
    def setUp(self):
        self.a, self.b = load_boards(HERE, filename=BUILD_FILE)
        self.sa, self.sb = self.a.lab.new_state(), self.b.lab.new_state()

    def poll(self, board, state):
        with serial() as out:
            board.lab.step(state)
        return out.getvalue()

    def test_sender_sees_ack(self):
        self.a.mb.button_a.click()
        self.assertEqual(self.poll(self.a, self.sa), "tx btn 1 A\n")
        self.assertEqual(self.poll(self.b, self.sb), "rx btn 1 A\n")
        self.assertEqual(self.poll(self.a, self.sa), "acked 1\n")
        self.assertEqual(self.b.radio.sent[-1], b"\x01\x00\x01ack:1:")

    def test_duplicate_is_acked_but_not_shown_twice(self):
        self.b.radio._inject_str("btn:1:A")
        self.b.radio._inject_str("btn:1:A")
        out = self.poll(self.b, self.sb) + self.poll(self.b, self.sb)
        self.assertEqual(out, "rx btn 1 A\n")
        self.assertEqual(len(self.b.radio.sent), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
