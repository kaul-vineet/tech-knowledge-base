"""Fitness function for ADR-020 (chaos runs as a bounded, automated campaign in CI). Keeps the decision true: every
saga experiment stays within the 10% blast radius and hurts at most ABORT_AFTER customers, and the hardened L300
targets keep every hypothesis on seeds 14-16 (a regression in solution_saga.py or solution_raft.py fails the build).
Default target = solution_chaos.py; BUILD_TARGET=mine checks chaos.py."""
import importlib.util, os, sys, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FILE = "chaos.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_chaos.py"
spec = importlib.util.spec_from_file_location("fitness_chaos", HERE / FILE)
ch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ch)


class ChaosFitness(unittest.TestCase):
    def test_experiments_are_bounded(self):
        for target in ch.SAGA:
            for fault in ("shipping-outage", "crash-after-charge"):
                r = ch.run_saga_experiment(target, fault, 14)
                with self.subTest(target=target, fault=fault):
                    self.assertLessEqual(r["blast_radius_pct"], 10.0)
                    self.assertLessEqual(r["customers_hurt"], ch.ABORT_AFTER)

    def test_hardened_targets_keep_every_hypothesis(self):
        for seed in (14, 15, 16):
            for fault in ("shipping-outage", "crash-after-charge"):
                self.assertTrue(ch.run_saga_experiment("L300 hardened", fault, seed)["held"])
            for fault in ("random-crash", "rolling-restart"):
                self.assertTrue(ch.run_raft_experiment("L300 hardened", fault, seed)["held"])


if __name__ == "__main__":
    unittest.main()
