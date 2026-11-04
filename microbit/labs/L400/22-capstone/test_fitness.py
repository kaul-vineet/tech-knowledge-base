"""Capstone fitness function: the whole scorecard passes on a seed the design was not tuned on."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_capstone  # noqa: E402


class Fitness(unittest.TestCase):
    def test_scorecard_passes_on_another_seed(self):
        lines, _ = run_capstone.scorecard(seed=23)
        card = [json.loads(line) for line in lines]
        failed = [c for c in card[:-1] if not c["pass"]]
        self.assertEqual(failed, [])
        self.assertEqual(card[-1]["scorecard"], "PASS")


if __name__ == "__main__":
    unittest.main(verbosity=2)
