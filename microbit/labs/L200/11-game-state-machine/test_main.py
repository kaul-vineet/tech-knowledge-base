import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab, serial  # noqa: E402
import microbit  # noqa: E402

STATES = ("idle", "play", "over")
EVENTS = ("a", "shake", "timeout")


class TransitionTable(unittest.TestCase):
    """The whole table, state x event: what the game does is data, so test it as data."""

    def setUp(self):
        self.lab = load_lab(HERE)

    def test_every_state_event_pair(self):
        expected = {
            ("idle", "a"): "play", ("idle", "shake"): "play", ("idle", "timeout"): "idle",
            ("play", "a"): "play", ("play", "shake"): "idle", ("play", "timeout"): "over",
            ("over", "a"): "idle", ("over", "shake"): "over", ("over", "timeout"): "over",
        }
        got = {(s, e): self.lab.next_state(s, e)[0] for s in STATES for e in EVENTS}
        self.assertEqual(got, expected)

    def test_every_target_is_a_known_state(self):
        for nxt, _ in self.lab.TRANSITIONS.values():
            self.assertIn(nxt, STATES)


class GameRun(unittest.TestCase):
    def setUp(self):
        self.lab = load_lab(HERE)
        self.game = self.lab.new_game()

    def poll(self):
        with serial() as out:
            self.lab.step(self.game)
        return out.getvalue()

    def test_round_with_hit_and_miss(self):
        microbit.button_a.click()
        self.assertEqual(self.poll(), "idle -> play (a)\n")               # t = 0
        microbit.sleep(600)                                                # dot at x = 2
        microbit.button_a.click()
        self.assertEqual(self.poll(), "hit 1\n")
        self.assertEqual(microbit.display.get_pixel(2, 2), 9)
        microbit.sleep(300)                                                # x = 3
        microbit.button_a.click()
        self.assertEqual(self.poll(), "miss 1\n")
        microbit.sleep(5100)                                               # t = 6000
        self.assertEqual(self.poll(), "play -> over (timeout)\nscore 1\n")
        microbit.button_a.click()
        self.assertEqual(self.poll(), "over -> idle (a)\n")

    def test_shake_starts_and_aborts(self):
        microbit.accelerometer.inject_gesture("shake")
        self.assertEqual(self.poll(), "idle -> play (shake)\n")
        microbit.accelerometer.inject_gesture("shake")
        self.assertEqual(self.poll(), "play -> idle (shake)\n")

    def test_not_over_one_ms_early(self):
        microbit.button_a.click()
        self.poll()
        microbit.sleep(5999)
        self.assertEqual(self.poll(), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
