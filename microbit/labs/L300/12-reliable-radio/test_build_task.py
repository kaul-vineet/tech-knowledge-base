"""Build task check (lab 12): ARQ delivers every reading exactly once, in order.

Runs solution.py. To check YOUR version: BUILD_FILE=main.py python -m unittest test_build_task
(Windows PowerShell: $env:BUILD_FILE="main.py"; py -m unittest test_build_task)
main.py as shipped FAILS this check: that is the failureLab "before".
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import link_sim  # noqa: E402

BUILD_FILE = os.environ.get("BUILD_FILE", "solution.py")
WANT = ["r%d" % i for i in range(1, 21)]


class ReliableLink(unittest.TestCase):
    def test_faulty_link_delivers_all_exactly_once(self):
        res = link_sim.run(BUILD_FILE, faults=link_sim.FAULTS)
        self.assertEqual(res["delivered"], WANT)

    def test_other_seeds_too(self):
        for seed in range(1, 6):
            faults = dict(link_sim.FAULTS, seed=seed)
            self.assertEqual(link_sim.run(BUILD_FILE, faults=faults)["delivered"], WANT, seed)

    def test_retransmits_are_visible_in_the_json_line(self):
        res = link_sim.run(BUILD_FILE, faults=link_sim.FAULTS)
        sender = json.loads(res["json"][0])
        self.assertGreater(sender["retx"], 0)
        self.assertEqual(sender["acked"], 20)

    def test_dead_link_gives_up_and_reports(self):
        res = link_sim.run(BUILD_FILE, n=2, faults=dict(loss=1.0, seed=1), run_ms=10000)
        self.assertEqual(res["delivered"], [])
        self.assertEqual(res["a"]["gave_up"], 2)          # 4.7 s per frame (100+200+400+5x800 ms), then move on


if __name__ == "__main__":
    unittest.main(verbosity=2)
