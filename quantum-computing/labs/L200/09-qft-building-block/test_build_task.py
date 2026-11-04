"""Build-task check for lab 09. Run: python -m unittest test_build_task -v

Checks solution_period.py by default; to check your own file set BUILD_TASK_MODULE, e.g.
  macOS:   BUILD_TASK_MODULE=my_period python -m unittest test_build_task -v
  Windows: $env:BUILD_TASK_MODULE = "my_period"; python -m unittest test_build_task -v
"""
import importlib
import importlib.util
import os
import unittest

mod = importlib.import_module(os.environ.get("BUILD_TASK_MODULE", "solution_period"))
HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None


class PeriodNumpy(unittest.TestCase):
    def test_periods_and_offsets(self):
        for n in (3, 4):
            for period in (1, 2, 4):
                for offset in range(period):
                    self.assertEqual(mod.period_numpy(n, period, offset)[0], period, (n, period, offset))

    def test_period_2_peaks(self):
        self.assertEqual(mod.period_numpy(3, 2)[1], {"000": 0.5, "100": 0.5})


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class PeriodSdk(unittest.TestCase):
    def test_qiskit_finds_period(self):
        for period, offset in ((2, 1), (4, 3)):
            self.assertEqual(mod.period_qiskit(3, period, offset)[0], period)


if __name__ == "__main__":
    unittest.main()
