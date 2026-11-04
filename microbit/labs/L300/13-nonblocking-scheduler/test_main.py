import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tap_sim  # noqa: E402


class HappyPath(unittest.TestCase):
    """main.py works when the user presses deliberately (the bench test)."""

    def test_deliberate_press_counts(self):
        state, out = tap_sim.run_blocking([(500, 1500)], until_ms=4000)
        self.assertEqual(tap_sim.tap_lines(out), ["tap 1"])

    def test_long_press_clears(self):
        state, out = tap_sim.run_blocking([(500, 1500), (3500, 4500)], until_ms=9000)
        self.assertEqual([l for l in out.splitlines() if l.startswith(("tap", "clear"))],
                         ["tap 1", "clear"])
        self.assertEqual(state["taps"], 0)

    def test_sensor_line_is_json_once_per_second(self):
        state, out = tap_sim.run_blocking([], until_ms=3000)
        rows = [json.loads(l) for l in out.splitlines() if l.startswith("{")]
        self.assertEqual([r["t"] for r in rows], [0, 1000, 2000])
        self.assertEqual(rows[0], {"t": 0, "temp": 20, "taps": 0})


if __name__ == "__main__":
    unittest.main(verbosity=2)
