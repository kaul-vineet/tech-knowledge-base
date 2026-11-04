"""buildTask check (lesson 17): update() must gate the innovation, so a sensor glitch cannot move the twin.

By default this checks solution/twin.py. To check your edited twin.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file 2 of 2 tests fail; after your fix both pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("twin.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/twin.py")
spec = importlib.util.spec_from_file_location("twin_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestInnovationGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.twin, cls.errors = target.run()

    def test_glitch_is_rejected_not_assimilated(self):
        first = self.twin.events[0]
        self.assertEqual((first["t_min"], first["event"]), (1250, "rejected"))

    def test_no_false_alarm_before_the_drift(self):
        self.assertEqual([e for e in self.twin.events if e["event"] == "drift_alarm" and e["t_min"] < 2500], [])


if __name__ == "__main__":
    unittest.main()
