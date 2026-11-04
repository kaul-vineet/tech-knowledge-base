"""Capstone fitness functions (ADRs 0001-0003): the search must keep finding the planets and nothing else.

1. Recovery: all 3 injected planets are planet_candidate with period error < 0.1 %.
2. False positives: 0 among the 9 other stars (2 eclipsing binaries, a spotted rotator, a ramp, 5 quiet stars).
3. Honest fits: every fitted depth within 3 sigma of the injected depth.
4. The agent never decides: run_capstone's scorecard is PASS and M6 published nothing the gate flagged.
"""
import json
import unittest

import run_capstone


def setUpModule():
    global RESULTS, TRUTH
    RESULTS, _ = run_capstone.analyse_all()
    TRUTH = json.loads((run_capstone.DATA / "truth.json").read_text(encoding="utf-8"))


class TestCapstoneFitness(unittest.TestCase):
    def test_recovery(self):
        for s, v in TRUTH.items():
            if v["kind"] == "planet":
                with self.subTest(star=s):
                    self.assertEqual(RESULTS[s]["verdict"], "planet_candidate")
                    self.assertLess(abs(RESULTS[s]["period_d"] / v["period_d"] - 1), 0.001)

    def test_no_false_positives(self):
        fps = [s for s, v in TRUTH.items() if v["kind"] != "planet" and RESULTS[s]["verdict"] == "planet_candidate"]
        self.assertEqual(fps, [])

    def test_depths_within_three_sigma(self):
        for s, v in TRUTH.items():
            if v["kind"] == "planet":
                fit = RESULTS[s]["fit"]
                self.assertLessEqual(abs(fit["depth_ppm"] - v["depth"] * 1e6), 3 * fit["depth_err_ppm"])

    def test_scorecard_pass_and_agent_gated(self):
        lines, final = run_capstone.main()
        self.assertEqual(final["scorecard"], "PASS")
        self.assertEqual(lines[-1]["published"], [])


if __name__ == "__main__":
    unittest.main()
