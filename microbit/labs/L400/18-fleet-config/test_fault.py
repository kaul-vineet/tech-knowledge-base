"""failureLab symptom (observed, seeded): one-phase config push to all six devices.

PASSES because it pins the failure: devices run versions the gateway never acknowledged, and the
bad v3 (radio group 99) leaves five devices deaf for good - only a re-flash brings them back.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fleet_sim  # noqa: E402


class Symptom(unittest.TestCase):
    def test_unacknowledged_configs_and_bricked_devices(self):
        m, _ = fleet_sim.run("config_agent.py", "push-all")
        self.assertEqual(m["unacked_ticks"], 12086)
        self.assertEqual("".join(str(v) for v in m["final"].values()), "333332")
        self.assertEqual(sorted(m["final_group"].values()), [18, 99, 99, 99, 99, 99])


if __name__ == "__main__":
    unittest.main(verbosity=2)
