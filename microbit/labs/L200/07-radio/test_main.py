import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_boards, load_lab, serial  # noqa: E402
import radio  # noqa: E402  (stub)


class MessageFormat(unittest.TestCase):
    def setUp(self):
        self.lab = load_lab(HERE)

    def test_encode_decode_round_trip(self):
        self.assertEqual(self.lab.encode("tmp", 3, 21), "tmp:3:21")
        self.assertEqual(self.lab.decode("tmp:3:21"), ("tmp", 3, "21"))

    def test_decode_rejects_garbage(self):
        for text in ("hello", "btn:x:A", "zzz:1:A", "btn:1:A:extra", ""):
            self.assertIsNone(self.lab.decode(text), text)

    def test_send_adds_string_header(self):
        state = self.lab.new_state()
        with serial() as out:
            self.lab.send(state, "btn", "A")
        self.assertEqual(radio.sent[-1], b"\x01\x00\x01btn:1:A")
        self.assertEqual(out.getvalue(), "tx btn 1 A\n")

    def test_raw_bytes_and_bad_text_are_counted_not_crashing(self):
        state = self.lab.new_state()
        radio._inject(b"\xff\x00")          # not a radio.send() string -> ValueError inside
        radio._inject_str("hello")           # a string, but not our format
        with serial() as out:
            self.lab.step(state)
            self.lab.step(state)
        self.assertEqual(out.getvalue(), "rx bad 1\nrx bad 2\n")

    def test_duplicates_are_dropped(self):
        state = self.lab.new_state()
        radio._inject_str("btn:1:A")
        radio._inject_str("btn:1:A")
        with serial() as out:
            self.lab.step(state)
            self.lab.step(state)
        self.assertEqual(out.getvalue(), "rx btn 1 A\n")


class TwoBoards(unittest.TestCase):
    def setUp(self):
        self.a, self.b = load_boards(HERE)
        self.sa, self.sb = self.a.lab.new_state(), self.b.lab.new_state()

    def run_both(self):
        with serial() as out:
            self.a.lab.step(self.sa)
            self.b.lab.step(self.sb)
        return out.getvalue()

    def test_button_on_a_shows_on_b(self):
        self.a.mb.button_a.click()
        self.assertEqual(self.run_both(), "tx btn 1 A\nrx btn 1 A\n")
        self.assertEqual(self.b.mb.display.last_text, "A")

    def test_temperature_from_b_reaches_a(self):
        self.b.mb._inject_temperature(23)
        self.b.mb.button_b.click()
        self.assertEqual(self.run_both(), "tx tmp 1 23\n")      # A polled before B sent
        self.assertEqual(self.run_both(), "rx tmp 1 23\n")

    def test_different_group_hears_nothing(self):
        self.b.radio.config(group=8)
        self.a.mb.button_a.click()
        self.assertEqual(self.run_both(), "tx btn 1 A\n")

    def test_queue_of_3_drops_the_4th(self):
        for _ in range(4):
            self.a.mb.button_a.click()
            with serial():
                self.a.lab.step(self.sa)
        self.assertEqual(self.b.radio.dropped, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
