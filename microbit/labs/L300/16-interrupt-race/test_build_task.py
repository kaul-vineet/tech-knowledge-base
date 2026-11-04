"""Build task check (lab 16): with a critical section no tick is ever lost.

Runs solution_model.py (the Python mirror of firmware/src/bin/fixed.rs).
To check YOUR version: BUILD_FILE=race_model.py python -m unittest test_build_task
(Windows PowerShell: $env:BUILD_FILE="race_model.py"; py -m unittest test_build_task)
race_model.py FAILS this check: that is the failureLab "before". The Rust
equivalents are logic/src/lib.rs tests (cargo test) and renode/interrupt_race.robot
(Renode) - both pending-ci.
"""
import importlib.util
import itertools
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import host_sim  # noqa: E402

BUILD_FILE = os.environ.get("BUILD_FILE", "solution_model.py")


def load():
    spec = importlib.util.spec_from_file_location("take_under_test", os.path.join(HERE, BUILD_FILE))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.take


class NoLostTicks(unittest.TestCase):
    def test_every_interleaving(self):
        take = load()
        points = ("before", "window", "after")
        for r in range(len(points) + 1):
            for fire in itertools.combinations(points, r):
                m = host_sim.schedule(take, set(fire))
                self.assertEqual(m.lost(), 0, fire)
                self.assertEqual(m.consumed + m.pending, m.isr_total, fire)

    def test_soak(self):
        m = host_sim.soak(load())
        self.assertEqual((m.isr_total, m.lost()), (1316, 0))

    def test_other_seeds(self):
        for seed in range(1, 11):
            self.assertEqual(host_sim.soak(load(), seed=seed).lost(), 0, seed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
