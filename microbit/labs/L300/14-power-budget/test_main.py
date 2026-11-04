import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab  # noqa: E402
import budget  # noqa: E402
import log  # noqa: E402
import microbit  # noqa: E402


class Logger(unittest.TestCase):
    def test_logs_every_100_ms_and_shows_value(self):
        lab = load_lab(HERE)
        state = lab.new_state()
        for _ in range(3):
            lab.loop_once(state)
        self.assertEqual(log.rows, ["Time (milliseconds),temp", "0,20", "100,20", "200,20"])
        self.assertEqual(microbit.display.last_text, "20")
        self.assertEqual(microbit.running_time(), 300)


class Model(unittest.TestCase):
    def test_always_on_is_battery_over_current(self):
        est = budget.estimate({"total_ms": 1000, "wakeups": 0})
        self.assertEqual(est, {"awake_pct": 100.0, "avg_ma": 30.0, "life_h": 41.7,   # 1250 / 30
                               "life_h_range": [41.7, 41.7], "chip_only_bound_h": 41.7})

    def test_duty_cycle_average(self):
        # 10 wake-ups x 20 ms in 10 s: 2% awake at 30 mA, 98% at the 0.5 mA board floor
        est = budget.estimate({"total_ms": 10000, "wakeups": 10})
        self.assertEqual(est["avg_ma"], round(0.02 * 30 + 0.98 * 0.5, 4))

    def test_headline_is_the_conservative_board_figure(self):
        est = budget.estimate({"total_ms": 3600000, "wakeups": 483})
        low, high = est["life_h_range"]
        self.assertEqual(est["life_h"], low)
        self.assertLess(high, est["chip_only_bound_h"])   # the chip floor is only an outer bound

    def test_every_figure_is_labelled_in_the_source(self):
        with open(os.path.join(HERE, "budget.py"), encoding="utf-8") as f:
            src = f.read()
        for label in ("UPPER BOUND", "BOARD SLEEP FLOOR", "CHIP ONLY", "ASSUMPTION", "Energizer E92"):
            self.assertIn(label, src)

    def test_window_is_exactly_one_hour(self):
        # the last 8 s sleep starts at 3,599,400 ms; it must not stretch the averaging window
        run = budget.run_design("solution.py")
        self.assertEqual((run["total_ms"], run["wakeups"]), (3600000, 483))
        est = budget.estimate(run)
        avg_low = (483 * 20 * 30.0 + (3600000 - 483 * 20) * 0.05) / 3600000
        self.assertEqual(est["life_h_range"], [2158.3, round(1250.0 / avg_low, 1)])
        self.assertEqual(est["life_h_range"][1], 9588.4)

    def test_report_is_one_json_line(self):
        d = json.loads(budget.report("main.py"))
        self.assertEqual(sorted(d), ["avg_ma", "awake_pct", "chip_only_bound_h", "design", "life_h",
                                     "life_h_range", "max_delay_ms", "meets_brief", "samples",
                                     "wakeups"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
