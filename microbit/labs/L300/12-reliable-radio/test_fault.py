"""failureLab symptom (observed, seeded): main.py on the faulty radio.

This test PASSES because it pins down the failure: 20% loss (+dup, reorder,
corrupt; seed 12) silently loses readings, and the sender's counters cannot tell.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import link_sim  # noqa: E402


class Symptom(unittest.TestCase):
    def test_readings_vanish_silently(self):
        res = link_sim.run("main.py", faults=link_sim.FAULTS)
        self.assertEqual(link_sim.summary(res), "delivered 14/20, missing ['r2', 'r8', 'r11', "
                         "'r13', 'r14', 'r20'], duplicates 2, in order False")
        self.assertEqual(res["a"], {"tx": 20, "rx": 0, "bad": 0, "delivered": 0})  # sender: "all sent"
        self.assertEqual(res["faults"]["lost"], 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
