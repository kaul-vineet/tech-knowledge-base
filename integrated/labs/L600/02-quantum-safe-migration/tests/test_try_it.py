import sys
import unittest

import _lab

sys.path.insert(0, str(_lab.LAB / "try_it"))
import experiments  # noqa: E402


class TestTryIt(unittest.TestCase):
    def test_horizon_sweep(self):
        sweep = experiments.horizon_sweep()
        self.assertEqual([len(sweep[z]) for z in (5, 10, 15)], [5, 3, 0])

    def test_bigger_signature_breaks_the_budget(self):
        r = experiments.bigger_signature()
        self.assertEqual((r["ok"], r["handshake_bytes"], r["delivered"]), (False, 7145, 6))


if __name__ == "__main__":
    unittest.main()
