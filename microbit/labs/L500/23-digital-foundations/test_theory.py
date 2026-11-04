"""Every theorem check in foundations1.py must pass (numbers quoted in content/L500.json as checkOutput)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import foundations1  # noqa: E402


class TheoremChecks(unittest.TestCase):
    pass


def _make(check):
    def test(self):
        ok, line = check()
        self.assertTrue(ok, line)
    return test


for _c in foundations1.CHECKS:
    setattr(TheoremChecks, "test_" + _c.__name__, _make(_c))


if __name__ == "__main__":
    unittest.main(verbosity=2)
