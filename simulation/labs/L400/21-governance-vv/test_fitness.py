"""Fitness function (lesson 21 ADR 0001): keeps "structured model card + machine-checked claims" true.

Re-runs the full evidence pack and fails the build if: the verification suite is not green; the committed
model_card.json has ANY finding (claims wider than evidence, stale code/data hash); or the validated envelope no
longer covers the busiest hour in arrivals.csv. Default target: solution/governance.py; BUILD_TARGET=mine checks
your governance.py (the shipped check_card() also passes the honest card - pair it with test_build_task).
"""
import importlib.util
import json
import os
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("governance.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/governance.py")
spec = importlib.util.spec_from_file_location("governance_fitness", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestGovernanceFitness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ev = target.evidence()
        cls.card = json.loads((HERE / "model_card.json").read_text(encoding="utf-8"))

    def test_verification_green(self):
        self.assertEqual(self.ev["verification"]["failures"], 0)

    def test_committed_card_matches_fresh_evidence(self):
        self.assertEqual(target.check_card(self.card, self.ev), [])

    def test_envelope_covers_the_busiest_hour(self):
        self.assertGreaterEqual(self.ev["envelope_rho_max"], self.ev["peak_utilisation"])

    def test_every_checklist_item_ticked(self):
        self.assertTrue(all(ok for _, ok in target.checklist(self.card, self.ev, [])))


if __name__ == "__main__":
    unittest.main()
