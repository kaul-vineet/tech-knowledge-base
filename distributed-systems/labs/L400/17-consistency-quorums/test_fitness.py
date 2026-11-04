"""Fitness function for ADR-017 (the config store runs N=3, R=2, W=2 + read write-back). Keeps the decision true:
on seeds 11-20 the history stays linearizable, read p99 stays within the 150 ms budget and region C can be lost.
Default target = solution_quorum.py; BUILD_TARGET=mine checks quorum.py."""
import importlib.util, os, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILE = "quorum.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_quorum.py"
spec = importlib.util.spec_from_file_location("fitness_quorum", HERE / FILE)
qm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qm)
READ_P99_BUDGET_MS, MIN_AVAIL_PCT = 150.0, 99.0


class ConfigStoreFitness(unittest.TestCase):
    def test_linearizable_fast_enough_and_survives_region_loss(self):
        for seed in range(11, 21):
            m = qm.measure(2, 2, True, seed=seed)
            with self.subTest(seed=seed):
                self.assertTrue(m["linearizable"], m)
                self.assertLessEqual(m["read_p99"], READ_P99_BUDGET_MS)
                self.assertGreaterEqual(m["avail_c_down_pct"], MIN_AVAIL_PCT)


if __name__ == "__main__":
    unittest.main()
