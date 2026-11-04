"""Build-task check for lab 21 (AST crypto inventory). Run: python -m unittest test_build_task -v

Checks solution_scanner.py by default. Your file: my_scanner.py with scan(root=...) -> sorted list of findings
  macOS:   BUILD_TARGET=mine python -m unittest test_build_task -v
  Windows: $env:BUILD_TARGET = "mine"; python -m unittest test_build_task -v
failureLab proof: BUILD_TASK_MODULE=pqc_lab (grep for 'rsa') FAILS 4 of 4 tests.
"""
import json
import unittest
from pathlib import Path

import buildtarget

mod = buildtarget.load("solution_scanner", "my_scanner")
EXPECTED = json.loads((Path(__file__).resolve().parent / "EXPECTED_INVENTORY.json").read_text(encoding="utf-8"))


class Inventory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.found = mod.scan()
        cls.locs = {(f["file"], f["line"]): f for f in cls.found}

    def test_matches_ground_truth(self):
        self.assertEqual(self.found, EXPECTED)

    def test_docstrings_are_not_findings(self):
        self.assertNotIn(("toy_app/auth.py", 1), self.locs)

    def test_aliased_and_from_imports_resolve(self):
        self.assertEqual(self.locs.get(("toy_app/auth.py", 11), {}).get("algorithm"), "ECDSA P-256")   # 'ec as curves'
        self.assertEqual(self.locs.get(("toy_app/sync.py", 7), {}).get("usage"), "key-establishment")  # from ...ec import ECDH

    def test_purpose_is_classified(self):
        self.assertEqual(self.locs.get(("toy_app/billing.py", 7), {}).get("usage"), "key-establishment")  # RSA-OAEP


if __name__ == "__main__":
    unittest.main()
