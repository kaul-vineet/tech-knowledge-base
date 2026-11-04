"""Build task check (lab 18): two-phase config with probation and automatic rollback.

Runs solution.py. Check YOUR file: BUILD_TARGET=mine python -m unittest test_build_task
(= config_agent.py, which FAILS as shipped; or BUILD_FILE=<file>). Windows PowerShell:
$env:BUILD_TARGET="mine"; py -m unittest test_build_task
"""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fleet_sim  # noqa: E402

TARGET = os.environ.get("BUILD_FILE") or ("config_agent.py" if os.environ.get("BUILD_TARGET") == "mine"
                                          else "solution.py")


class TwoPhase(unittest.TestCase):
    def test_never_runs_an_unacknowledged_config(self):
        for strategy in ("push-all", "staged"):
            m, _ = fleet_sim.run(TARGET, strategy)
            self.assertEqual(m["unacked_ticks"], 0, strategy)

    def test_bad_config_rolls_back_everywhere(self):
        m, fleet = fleet_sim.run(TARGET, "push-all")
        self.assertEqual(list(m["final"].values()), [2] * 6)        # good v2 kept, bad v3 gone
        self.assertEqual(set(m["final_group"].values()), {18})       # nobody left deaf
        self.assertEqual([j["status"] for j in m["jobs"]], ["done", "halted"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
