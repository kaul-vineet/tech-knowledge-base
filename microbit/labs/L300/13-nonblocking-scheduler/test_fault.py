"""failureLab symptom (observed, seeded): quick taps vanish in the blocking loop."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tap_sim  # noqa: E402


class Symptom(unittest.TestCase):
    def test_quick_taps_are_missed(self):
        presses = tap_sim.taps()
        self.assertEqual([t for t, _ in presses], [932, 1680, 2630, 3695, 4645, 5655, 6689, 7744])
        state, out = tap_sim.run_blocking(presses)
        self.assertEqual(state["taps"], 1)            # 8 taps, 1 counted, no error anywhere
        self.assertEqual(tap_sim.tap_lines(out), ["tap 1"])   # only the 932 ms tap covers a sample (t=1000)
        self.assertNotIn("Traceback", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
