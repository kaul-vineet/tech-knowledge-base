"""The two tryIt experiments give the documented results."""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _fixture  # noqa: E402
import unittest  # noqa: E402

import pipeline  # noqa: E402
import registry  # noqa: E402

crn = runpy.run_path(str(_fixture.LAB / "try_it" / "crn.py"))


class TestTryIt(unittest.TestCase):
    def test_crn_needs_far_fewer_replications(self):
        n, m, hw, r = crn["paired"]()
        self.assertEqual(n, 10)
        self.assertLessEqual(hw, 0.3)
        self.assertGreater(r, 0.9)

    def test_tighter_target_stops_at_the_budget(self):
        pl = pipeline.Pipeline(registry.Registry(), pipeline.SimBudget(250_000), half_width=0.2)
        r = pl.submit("run_experiment", {"baseline": _fixture.A, "candidate": _fixture.B, "replications": 3, "seed": 13})
        self.assertTrue(r["budget_limited"])
        self.assertEqual((r["replications"], r["required_replications"]), (10, 105))
        self.assertLessEqual(pl.budget.spent, 250_000)


if __name__ == "__main__":
    unittest.main()
