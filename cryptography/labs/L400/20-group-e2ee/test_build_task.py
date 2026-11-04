"""Build task check (failureLab proof). Default: tests solution_remove.py.
Test YOUR version (the shipped group_keys.py forgets to blank the removed member's path):
  macOS    BUILD_TARGET=mine python -m unittest -v test_build_task
  Windows  $env:BUILD_TARGET="mine"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_TARGET
BUILD_IMPL=<module> picks any other module."""
import importlib
import itertools
import os
import random
import unittest

MODULE = "group_keys" if os.environ.get("BUILD_TARGET") == "mine" else os.environ.get("BUILD_IMPL", "solution_remove")
impl = importlib.import_module(MODULE)
NAMES = ["alice", "bob", "carol", "dave", "erin", "frank", "grace", "heidi"]


class TestRemovalExcludes(unittest.TestCase):
    def test_seeded_removal_from_the_lab(self):
        rng = random.Random(20)
        g = impl.Group(NAMES)
        g.commit("carol")
        removed, committer = rng.choice(NAMES[1:4]), rng.choice(NAMES[4:])
        g.commit(committer, remove=removed)
        msg = g.send(committer, "after removal")
        self.assertIsNone(g.read(removed, msg))
        self.assertTrue(all(g.read(n, msg) for n in NAMES if n != removed))

    def test_every_committer_removed_pair(self):
        leaks = []
        for committer, removed in itertools.permutations(NAMES, 2):
            g = impl.Group(NAMES)
            g.commit(committer, remove=removed)
            if g.read(removed, g.send(committer, "x")) is not None:
                leaks.append((committer, removed))
        self.assertEqual(leaks, [])


if __name__ == "__main__":
    unittest.main()
