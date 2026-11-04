"""Build-task check: an idempotent consumer charges each message id exactly once despite redeliveries.
Default target = solution_broker.py. Test YOUR broker.py:  BUILD_TARGET=mine python -m unittest test_build_task -v
(PowerShell: $env:BUILD_TARGET="mine"; python -m unittest test_build_task -v)"""
import importlib.util, os, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILE = "broker.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_broker.py"
spec = importlib.util.spec_from_file_location("target_broker", HERE / FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestIdempotentConsumer(unittest.TestCase):
    def test_exactly_one_charge_per_message_across_seeds(self):
        for seed in (4, 8, 9, 22):  # seeds whose plain run has 3-5 duplicate charges
            out = mod.run(seed=seed, quiet=True)
            ids = [i for i, _ in out["ledger"]]
            self.assertEqual(len(ids), len(set(ids)), f"seed {seed}: duplicate charge")
            self.assertEqual(len(ids), 6)

    def test_duplicates_are_still_acked_and_poison_still_dead_lettered(self):
        out = mod.run(quiet=True)
        self.assertTrue(any("duplicate" in line for line in out["log"]))
        self.assertEqual(out["dlq"], ["poison"])


if __name__ == "__main__":
    unittest.main()
