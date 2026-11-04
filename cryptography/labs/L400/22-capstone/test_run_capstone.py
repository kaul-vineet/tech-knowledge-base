"""End to end: run_capstone.run() must pass every milestone (the scorecard is decided by code)."""
import unittest

import run_capstone


class TestScorecard(unittest.TestCase):
    def test_all_milestones_pass(self):
        rows = run_capstone.run()
        self.assertEqual([r["milestone"].split()[0] for r in rows if not r["pass"]], [])
        self.assertEqual(len(rows), 6)


if __name__ == "__main__":
    unittest.main()
