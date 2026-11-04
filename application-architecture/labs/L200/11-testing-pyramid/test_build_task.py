"""Build task check: `pyramid.py --budget` fails when a layer's mean test time exceeds its budget.

By default this checks solution/pyramid.py. To check your edited pyramid.py instead:
    CHECK_MINE=1 python -m unittest test_build_task -v        (PowerShell: $env:CHECK_MINE = "1")
"""
import contextlib
import importlib.util
import io
import os
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / ("pyramid.py" if os.environ.get("CHECK_MINE") else "solution/pyramid.py")
spec = importlib.util.spec_from_file_location("pyramid_under_test", TARGET)
pyramid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pyramid)


def rows(unit, integration, e2e):
    return {"unit": {"tests": 8, "mean_ms": unit}, "integration": {"tests": 4, "mean_ms": integration},
            "e2e": {"tests": 1, "mean_ms": e2e}}


class BudgetTest(unittest.TestCase):
    def test_within_budget(self):
        self.assertEqual(pyramid.budget_problems(rows(0.5, 120, 900)), [])

    def test_slow_unit_layer_is_reported(self):
        self.assertEqual(pyramid.budget_problems(rows(42.0, 120, 900)),
                         ["unit: mean 42.00 ms is over the 10 ms budget"])

    def test_custom_budgets(self):
        self.assertEqual(len(pyramid.budget_problems(rows(1, 120, 900), {"unit": 0.1, "integration": 50})), 2)

    def test_real_suite_meets_the_default_budget(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = pyramid.main(["--budget"], start_dir=HERE)
        self.assertEqual(code, 0, out.getvalue())
        self.assertIn("pyramid OK", out.getvalue())


if __name__ == "__main__":
    unittest.main()
