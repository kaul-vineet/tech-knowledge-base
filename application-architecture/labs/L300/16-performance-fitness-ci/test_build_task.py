"""Build task check (lesson 16): the overdue report uses a constant number of queries and returns the same rows.

By default this checks solution/loans_repo.py. To check your edited loans_repo.py instead:
    CHECK_MINE=1 python -m unittest test_build_task -v        (PowerShell: $env:CHECK_MINE = "1")
"""
import importlib.util
import os
import pathlib
import unittest

import fitness
import loans_repo as reference

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / ("loans_repo.py" if os.environ.get("CHECK_MINE") else "solution/loans_repo.py")
spec = importlib.util.spec_from_file_location("loans_repo_under_test", TARGET)
repo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(repo)


class QueryBudgetTest(unittest.TestCase):
    def test_query_count_does_not_grow_with_the_data(self):
        gate = fitness.gate_query_count(repo)
        self.assertTrue(gate["ok"], f"statements per report: {gate['value']}, budget {gate['budget']}")

    def test_same_rows_as_before_the_fix(self):
        for loans in (10, 500):
            self.assertEqual(repo.overdue_report(repo.seeded_db(loans=loans)),
                             reference.overdue_report(reference.seeded_db(loans=loans)))

    def test_all_fitness_gates_pass(self):
        results = [fitness.gate_import_boundaries(), fitness.gate_query_count(repo), fitness.gate_microbenchmark(repo)]
        self.assertEqual([r["gate"] for r in results if not r["ok"]], [])


if __name__ == "__main__":
    unittest.main()
