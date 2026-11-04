"""Fitness function for ADR-019 (majority-sync, leader in the region place_leader() picks). Keeps the decision true:
on seeds 19-28 the design meets the brief (us/eu write p99 <= 350 ms, RPO 0, RTO <= 5 s, no conflicts) and the
leader is still the best-placed region for today's traffic. Default target = solution_multiregion.py; BUILD_TARGET=mine."""
import importlib.util, os, sys, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FILE = "multiregion.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_multiregion.py"
spec = importlib.util.spec_from_file_location("fitness_multiregion", HERE / FILE)
mr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mr)


class MultiRegionFitness(unittest.TestCase):
    def test_brief_holds_on_ten_seeds(self):
        for seed in range(19, 29):
            with self.subTest(seed=seed):
                self.assertEqual(mr.violations(mr.evaluate(mr.DESIGN, seed)), [])

    def test_leader_is_still_best_placed(self):
        for seed in (19, 20, 21):
            self.assertEqual(mr.place_leader(mr.DESIGN["replication"], seed), mr.DESIGN["leader"])


if __name__ == "__main__":
    unittest.main()
