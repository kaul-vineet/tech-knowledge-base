import pathlib
import shutil
import tempfile
import unittest

import fitness_tenant
import tenancy
from app import HERE, measure, use_repository

TENANTS = [f"lib{i:02d}" for i in range(6)]


class LayoutTest(unittest.TestCase):
    """Measured with 6 tenants (app.py uses 50); the counts scale with the tenant count."""

    @classmethod
    def setUpClass(cls):
        use_repository(HERE / "repository.py")  # the shipped (unfixed) repository
        cls.rows = {}
        for layout_cls in tenancy.LAYOUTS:
            work = pathlib.Path(tempfile.mkdtemp(prefix=".tmp-", dir=HERE))
            try:
                row = measure(layout_cls, work, TENANTS)
            finally:
                shutil.rmtree(work, ignore_errors=True)
            cls.rows[row["layout"]] = row

    def test_symptom_shared_schema_leaks_other_tenants(self):
        self.assertEqual(self.rows["shared-schema"]["isolation"], {"rows": 84, "leaked": 70, "guard_violations": 1})

    def test_separate_tables_or_files_contain_the_bug_but_the_guard_still_sees_it(self):
        for kind in ("schema-per-tenant", "db-per-tenant"):
            self.assertEqual(self.rows[kind]["isolation"], {"rows": 14, "leaked": 0, "guard_violations": 1})

    def test_noisy_neighbour_only_separate_files_isolate_writes(self):
        blocked = {k: r["noisy_neighbour"]["blocked"] for k, r in self.rows.items()}
        self.assertEqual(blocked, {"shared-schema": 20, "schema-per-tenant": 20, "db-per-tenant": 0})

    def test_migration_effort(self):
        effort = {k: (r["migration"]["ddl_statements"], r["migration"]["files"]) for k, r in self.rows.items()}
        self.assertEqual(effort, {"shared-schema": (1, 1), "schema-per-tenant": (6, 1), "db-per-tenant": (6, 6)})


class GuardTest(unittest.TestCase):
    def test_static_gate_flags_the_new_report(self):
        result = fitness_tenant.gate()
        self.assertFalse(result["ok"])
        self.assertIn("WHERE due < ?", result["value"][0])

    def test_static_gate_passes_on_scoped_sql(self):
        self.assertTrue(fitness_tenant.gate([HERE / "solution" / "repository.py"])["ok"])


if __name__ == "__main__":
    unittest.main()
