"""Build task check (lesson 18): every loans query is scoped by tenant_id, statically and at runtime.

By default this checks solution/repository.py. To check your edited repository.py instead:
    CHECK_MINE=1 python -m unittest test_build_task -v        (PowerShell: $env:CHECK_MINE = "1")
"""
import os
import pathlib
import shutil
import tempfile
import unittest

import fitness_tenant
import tenancy
from app import HERE, use_repository

TARGET = HERE / ("repository.py" if os.environ.get("CHECK_MINE") else "solution/repository.py")


class TenantScopeTest(unittest.TestCase):
    def setUp(self):
        self.repo = use_repository(TARGET)
        self.work = pathlib.Path(tempfile.mkdtemp(prefix=".tmp-", dir=HERE))
        self.addCleanup(shutil.rmtree, self.work, True)
        self.layout = tenancy.SharedSchema(self.work)
        tenancy.seed(self.layout, ["lib00", "lib01", "lib02"], loans_per_tenant=9)

    def test_static_gate(self):
        result = fitness_tenant.gate([TARGET])
        self.assertTrue(result["ok"], result["value"])

    def test_overdue_report_sees_only_its_tenant(self):
        check = tenancy.leak_check(self.layout, "lib01")
        self.assertEqual(check, {"rows": 3, "leaked": 0, "guard_violations": 0})

    def test_every_repository_call_passes_the_guard(self):
        s = self.layout.session("lib02")
        self.addCleanup(s.conn.close)
        with tenancy.TenantGuard(s) as guard:
            self.repo.borrow(s, "lib02-m1", "b-new", "2026-11-30")
            self.repo.member_loans(s, "lib02-m1")
            self.repo.overdue(s, "2026-10-28")
        self.assertEqual(guard.violations, [])


if __name__ == "__main__":
    unittest.main()
