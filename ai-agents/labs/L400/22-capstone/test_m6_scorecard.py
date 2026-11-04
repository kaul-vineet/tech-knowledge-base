"""Milestone 6 (fitness: eval gate): the whole run with seeded faults, the scorecard, and the CI gate."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eval_capstone  # noqa: E402
import run_capstone  # noqa: E402


class M6Scorecard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            cls.rows, cls.effects, cls.spans = run_capstone.run(d)

    def test_scorecard(self):
        card = run_capstone.scorecard(self.rows, self.effects, self.spans)
        self.assertTrue(card["pass"], card)
        self.assertEqual({k: card[k] for k in ("severity_by_policy", "duplicate_effects", "effects_not_decided",
                                               "rollbacks_without_approval", "decided_without_model", "crash_restarts",
                                               "effects", "eval_gate")},
                         {"severity_by_policy": 8, "duplicate_effects": 0, "effects_not_decided": 0,
                          "rollbacks_without_approval": 0, "decided_without_model": 1, "crash_restarts": 1,
                          "effects": 11, "eval_gate": "PASS"})

    def test_gate_blocks_a_policy_regression(self):
        rows = copy.deepcopy(self.rows)
        rows[2]["severity"] = "SEV2"  # e.g. someone lowered a threshold and INC-3 now pages people
        report, reasons = eval_capstone.evaluate(rows)
        self.assertEqual(reasons, ["pass rate 88% < 100%", "regressions vs baseline: ['INC-3']"])


if __name__ == "__main__":
    unittest.main()
