"""Build task check (lesson 19): librarians may only act inside their own library; all policy gates pass.

By default this checks solution/loans.rego. To check your edited policy/loans.rego instead:
    CHECK_MINE=1 python -m unittest test_build_task -v        (PowerShell: $env:CHECK_MINE = "1")
"""
import os
import pathlib
import unittest

import fitness_policy
from rego_lite import DecisionPoint, load_policy

HERE = pathlib.Path(__file__).resolve().parent
POLICY = load_policy(HERE / ("policy" if os.environ.get("CHECK_MINE") else "solution") / "loans.rego")


class LibrarianScopeTest(unittest.TestCase):
    def test_librarian_of_another_library_is_denied(self):
        inp = {"action": "view", "subject": {"id": "s9", "tenant": "lib01", "roles": ["librarian"]},
               "resource": {"tenant": "lib00", "member_id": "m2", "active_loans": 1}}
        self.assertFalse(DecisionPoint(POLICY).decide(inp)["allowed"])

    def test_librarian_of_the_same_library_still_works(self):
        inp = {"action": "borrow", "subject": {"id": "s1", "tenant": "lib00", "roles": ["librarian"]},
               "resource": {"tenant": "lib00", "member_id": "m2", "active_loans": 7}}
        self.assertTrue(DecisionPoint(POLICY).decide(inp)["allowed"])

    def test_all_policy_gates(self):
        results = [fitness_policy.gate_policy_tests(POLICY), fitness_policy.gate_rule_coverage(POLICY)]
        self.assertEqual([r["value"] for r in results], [[], []])


if __name__ == "__main__":
    unittest.main()
