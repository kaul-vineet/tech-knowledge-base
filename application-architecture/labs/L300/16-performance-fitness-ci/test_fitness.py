import io
import shutil
import unittest
from datetime import date

import fitness
import loans_repo as base
from domain import days_overdue, fine
from failure_lab import HERE


class DomainTest(unittest.TestCase):
    def test_days_and_fine(self):
        self.assertEqual(days_overdue(date(2026, 10, 1), date(2026, 10, 28)), 27)
        self.assertEqual(days_overdue(date(2026, 11, 1), date(2026, 10, 28)), 0)
        self.assertEqual((fine(3), fine(100)), (0.75, 10.0))  # capped


class ReportTest(unittest.TestCase):
    def test_report_rows(self):
        rows = base.overdue_report(base.seeded_db(loans=10))
        self.assertEqual(len(rows), 5)  # 11 statements = 1 + 2 x 5 rows
        self.assertEqual(set(rows[0]), {"loan", "member", "book", "days", "fine"})
        self.assertTrue(all(r["days"] > 0 for r in rows))


class GateTest(unittest.TestCase):
    def test_query_counter_sees_every_statement(self):
        conn = base.seeded_db(loans=10)
        with fitness.QueryCounter(conn) as counter:
            conn.execute("SELECT 1").fetchall()
            conn.execute("SELECT 2").fetchall()
        self.assertEqual(counter.statements, ["SELECT 1", "SELECT 2"])

    def test_symptom_query_count_grows_with_the_data(self):
        self.assertEqual(fitness.gate_query_count(base)["value"], {10: 11, 500: 337})
        self.assertFalse(fitness.gate_query_count(base)["ok"])

    def test_import_gate_passes_and_catches_a_planted_import(self):
        self.assertTrue(fitness.gate_import_boundaries()["ok"])
        work = HERE / ".test-work"
        work.mkdir(exist_ok=True)
        self.addCleanup(shutil.rmtree, work, True)
        (work / "domain.py").write_text("import sqlite3\nfrom http_api import start\n", encoding="utf-8")
        self.assertEqual(fitness.gate_import_boundaries(work)["value"],
                         ["domain.py imports http_api", "domain.py imports sqlite3"])

    def test_response_time_gate_has_no_errors(self):
        result = fitness.gate_response_time(base)
        self.assertEqual((result["value"]["requests"], result["value"]["errors"]), (40, 0))

    def test_main_exit_code_is_the_ci_contract(self):
        self.assertEqual(fitness.main([], out=io.StringIO()), 1)  # base: query-count fails


if __name__ == "__main__":
    unittest.main()
