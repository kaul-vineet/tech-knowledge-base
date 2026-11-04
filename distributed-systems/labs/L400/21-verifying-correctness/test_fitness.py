"""Fitness function for ADR-021 (protocol changes are model-checked; store histories are checked for
linearizability). Keeps the decision true: the election model has no reachable violation of any invariant, and lab 17's
config setting (R=2 W=2 + write-back) produces linearizable histories on seeds 11-13. Default target =
solution_modelcheck.py; BUILD_TARGET=mine checks modelcheck.py."""
import importlib.util, os, unittest
from pathlib import Path

import lincheck

HERE = Path(__file__).resolve().parent
FILE = "modelcheck.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_modelcheck.py"
spec = importlib.util.spec_from_file_location("fitness_modelcheck", HERE / FILE)
mc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mc)


class VerificationFitness(unittest.TestCase):
    def test_protocol_has_no_reachable_violation(self):
        violated, trace, states, _ = mc.bfs()
        self.assertIsNone(violated, trace)
        self.assertGreater(states, 1000)  # the search really explored the space

    def test_config_store_histories_are_linearizable(self):
        store = lincheck.load_lab17("solution_quorum")
        for seed in (11, 12, 13):
            self.assertTrue(lincheck.check(store.run(2, 2, seed, write_back=True))[0], seed)


if __name__ == "__main__":
    unittest.main()
