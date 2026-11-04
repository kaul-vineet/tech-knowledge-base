"""Fitness functions: claims traced, runs reproducible bit-for-bit, budget never exceeded."""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _fixture  # noqa: E402
import unittest  # noqa: E402

import claims  # noqa: E402
import pipeline  # noqa: E402
import registry  # noqa: E402


class TestFitness(unittest.TestCase):
    def test_claims_traced(self):
        reg, _, _, _, published = _fixture.session()
        found, traced = claims.traced_runs(published, reg)
        self.assertGreater(found, 0)
        self.assertEqual(traced, found)

    def test_runs_reproducible(self):
        reg = _fixture.session()[0]
        self.assertTrue(all(registry.reproduce(r) for r in reg.runs()))
        unseeded = _fixture.session("unseeded")[0].runs()[0]
        self.assertFalse(registry.reproduce(unseeded))  # the fault the fitness function exists to catch

    def test_budget_never_exceeded(self):
        rng = random.Random(600)
        for limit in (20_000, 45_000, 90_000):
            pl = pipeline.Pipeline(registry.Registry(), pipeline.SimBudget(limit), half_width=0.3)
            for _ in range(6):  # adversarial mix of proposals, some unaffordable
                if rng.random() < 0.4:
                    pl.submit("run_screening", {"method": rng.choice(["morris", "sobol"]), "size": rng.choice([2, 5, 50])})
                else:
                    pl.submit("run_experiment", {"baseline": {"lam": 0.7, "mu": 1.0}, "candidate": {"lam": 0.7, "mu": 1.1},
                                                 "replications": rng.choice([2, 5, 12]), "seed": rng.randrange(100)})
            self.assertLessEqual(pl.budget.spent, limit)
            self.assertEqual(sum(a for _, a in pl.budget.ledger), pl.budget.spent)
            self.assertEqual(sum(registry.model.cost(r["params"]) for r in pl.registry.runs()), pl.budget.spent)


if __name__ == "__main__":
    unittest.main()
