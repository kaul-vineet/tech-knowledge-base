"""buildTask check (lesson 7): match_one_to_one() must leave every A source with at most one B partner.

By default this checks solution/crossmatch.py. To check your edited crossmatch.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfinished) file 1 of 3 tests fails; after your change all 3 pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("crossmatch.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/crossmatch.py")
spec = importlib.util.spec_from_file_location("crossmatch_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestOneToOne(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a, cls.b, cls.truth = target.make_catalogues()
        cls.idx, cls.sep = target.match_one_to_one(cls.a, cls.b)

    def test_no_a_source_claimed_twice(self):
        used = self.idx[self.idx >= 0]
        self.assertEqual(len(used), len(set(used.tolist())))

    def test_true_counterparts_mostly_kept(self):
        self.assertGreaterEqual(int(np.sum(self.idx[:len(self.truth)] == self.truth)), 1800)

    def test_kept_pairs_inside_radius(self):
        self.assertLessEqual(np.nanmax(self.sep), 1.0)


if __name__ == "__main__":
    unittest.main()
