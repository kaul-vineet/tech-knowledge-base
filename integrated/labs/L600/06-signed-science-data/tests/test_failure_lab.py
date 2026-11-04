"""Failure lab: mirror m2 'normalises' JSON through a stack that prints doubles with '%.17g'.
Same values, different bytes -> different SHA-256 -> mirrors never converge and clients reject what they serve.
test_fault_reproduces keeps the lab reproducible; test_fixed_with_jcs is the fix (m2 re-encodes with RFC 8785)."""
import json
import unittest

from _world import world

import checks
import run_project


class FailureLab(unittest.TestCase):
    def test_fault_reproduces(self):
        w = world("float-format")
        ok, d = checks.m4_replicated(w)
        self.assertFalse(ok)
        self.assertIsNone(d["rounds"][1])  # never converged in 20 rounds
        self.assertTrue(any(k.endswith("catalogue.json") for k in d["conflicts"]))
        ok, d = checks.m5_client(w)
        self.assertFalse(ok)
        self.assertTrue(any("catalogue.json missing or changed" in r for r in d["rejected"].values()))
        diff = run_project.diagnose(w)
        self.assertNotEqual(diff["m0"], diff["m2"])
        self.assertEqual(json.loads("[" + diff["m0"].split(":")[1].split(",")[0] + "]"),
                         json.loads("[" + diff["m2"].split(":")[1].split(",")[0] + "]"))  # same number, other bytes

    def test_fixed_with_jcs(self):
        w = world()
        self.assertTrue(checks.m4_replicated(w)[0])
        self.assertTrue(checks.s1_canonical(w)[0])
        self.assertIsNone(run_project.diagnose(w))


if __name__ == "__main__":
    unittest.main()
