"""Failure lab: last-writer-wins keyed by the device wall clock loses readings when device clocks step back
(d07 reboots; g2's acks carry a clock 300 s slow). Dots (dev, boot, seq) lose none.

BEFORE the fix:  FLEET_STORE=lww python -m unittest tests.test_failure_lab    -> test_no_reading_lost FAILS
AFTER (default): python -m unittest tests.test_failure_lab                    -> OK
(PowerShell: $env:FLEET_STORE="lww"; py -m unittest tests.test_failure_lab)
"""
import os
import unittest

from tests._shared import run

STORE = os.environ.get("FLEET_STORE", "dots")
INJECT = "wallclock-lww" if STORE == "lww" else None


class FailureLab(unittest.TestCase):
    def test_no_reading_lost_under_clock_skew(self):
        r = run(inject=INJECT)
        self.assertGreater(r["wall_key_repeats"], 0, "the clock fault must be present for the test to mean anything")
        self.assertEqual(r["lost"], 0, "lost %d readings with store=%s" % (r["lost"], STORE))

    def test_the_injected_fault_reproduces(self):
        r = run(inject="wallclock-lww")
        self.assertEqual(r["lost"], r["wall_key_repeats"])   # every repeated (dev, wall second) lost a row
        self.assertGreater(r["lost"], 1000)
        self.assertTrue(r["replicas_equal"])                 # converged - on the wrong data: no alarm fires
        lost_devs = {d[0] for d in set(r["truth"]) - r["stores"]["b1"].dots()}
        self.assertIn(7, lost_devs)                          # the reboot


if __name__ == "__main__":
    unittest.main()
