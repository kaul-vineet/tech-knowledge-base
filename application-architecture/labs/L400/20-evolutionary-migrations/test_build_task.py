"""Build task check (lesson 20): the contract step waits until no running instance uses the old column.

By default this checks solution/migrations.py. To check your edited migrations.py instead:
    CHECK_MINE=1 python -m unittest test_build_task -v        (PowerShell: $env:CHECK_MINE = "1")
"""
import importlib.util
import os
import pathlib
import unittest

import rollout

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / ("migrations.py" if os.environ.get("CHECK_MINE") else "solution/migrations.py")
spec = importlib.util.spec_from_file_location("migrations_under_test", TARGET)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ContractGuardTest(unittest.TestCase):
    def test_refuses_while_v2_instances_run(self):
        db = m.connect()
        m.expand(db)
        ok, reasons = m.can_contract(db, [2, 2, 3, 3])
        self.assertFalse(ok)
        self.assertTrue(any("v2" in r for r in reasons), reasons)

    def test_allows_when_backfilled_and_all_on_v3(self):
        db = m.connect()
        m.expand(db)
        self.assertEqual(m.can_contract(db, [3, 3, 3, 3]), (True, []))

    def test_zero_failed_requests_and_old_column_gone(self):
        r, rows = rollout.expand_contract(m)
        self.assertEqual(r.errors, 0, r.log[:3])
        self.assertNotIn("name", rows[-1]["columns"])


if __name__ == "__main__":
    unittest.main()
