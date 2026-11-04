"""Capstone fitness functions (ADRs 0001-0003): the decisions stay true while the code changes.

1. SLA: the recommended plan, simulated as whole days (24 reps, independent streams), keeps every hour's
   service-level lower bound >= 0.80 and mean abandonment <= 5%.
2. Reproducibility: the parallel runner stores identical results for 1 vs 2 workers.
3. Governance: the committed model card still describes this code and data (no findings).
4. Twin: no alarm before the surge; alarm within 90 minutes of it.
"""
import tempfile
import unittest
from pathlib import Path

import demand_twin
import governance_pack
import make_data
import pipeline
import runner

INP = pipeline.model_inputs(pipeline.history())


class TestCapstoneFitness(unittest.TestCase):
    def test_sla_holds_for_the_recommended_plan(self):
        staff = pipeline.plan(INP["rates"], INP, 4.5)
        tasks = [((r,), INP["rates"], staff, INP["mean_service"], INP["cv"], 4.5) for r in range(24)]
        with tempfile.TemporaryDirectory() as tmp:
            one, two = Path(tmp) / "one.db", Path(tmp) / "two.db"
            runner.run(one, tasks, workers=1)
            runner.run(two, tasks, workers=2)
            _, low, ab = runner.hourly_summary(one)
            self.assertGreaterEqual(min(low), pipeline.SL_TARGET)
            self.assertLessEqual(max(ab), pipeline.ABANDON_MAX)
            self.assertEqual(runner.checksum(one), runner.checksum(two))

    def test_governance_card_is_current(self):
        ev = {"inputs": INP, "validation": pipeline.validate(INP, 4.5)}
        self.assertEqual(governance_pack.check(governance_pack.load_card(), ev), [])

    def test_twin_alarm_timing(self):
        _, alarms = demand_twin.replay(INP["rates"])
        surge = 60 * make_data.SURGE_FROM_H
        self.assertTrue(alarms)
        self.assertTrue(all(a["t_min"] >= surge for a in alarms))
        self.assertLessEqual(alarms[0]["t_min"] - surge, 90)


if __name__ == "__main__":
    unittest.main()
