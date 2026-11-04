"""Fitness function: no hard-coded algorithm outside the registry (threshold: 0 violations).
Runs the static check over this lab (and the capstone services when present), and proves the check bites."""
import unittest
from pathlib import Path

import agility_lint

HERE = Path(__file__).resolve().parent
CAPSTONE = HERE.parent / "22-capstone"


class TestAgilityFitness(unittest.TestCase):
    def test_lab_has_no_hard_coded_algorithms(self):
        self.assertEqual(agility_lint.scan([HERE]), [])

    def test_capstone_services_have_no_hard_coded_algorithms(self):
        if not CAPSTONE.exists():
            self.skipTest("capstone not present")
        self.assertEqual(agility_lint.scan([CAPSTONE]), [])

    def test_check_catches_each_kind_of_violation(self):
        bad = ("from cryptography.hazmat.primitives.ciphers.aead import AESGCM\n"
               "box = AESGCM(key)\n"
               "header = {'aead': 'A256GCM'}\n")
        kinds = sorted(v[2].split()[0] for v in agility_lint.scan_source(bad, "bad.py"))
        self.assertEqual(kinds, ["hard-codes", "imports", "names"])


if __name__ == "__main__":
    unittest.main()
