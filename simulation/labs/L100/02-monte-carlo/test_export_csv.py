import csv
import unittest
from pathlib import Path

import numpy as np

import export_csv


class TestExportCsv(unittest.TestCase):
    def test_csv_has_same_samples_as_the_lab(self):
        path = Path(__file__).with_name("_test_mc_totals.csv")
        try:
            totals = export_csv.export(path, n=1_000, seed=42)
            with path.open(encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 1_000)
            back = np.array([float(r["total_days"]) for r in rows])
            np.testing.assert_allclose(back, totals, atol=1e-6)
        finally:
            path.unlink(missing_ok=True)

    def test_full_export_percentiles_match_readme(self):
        path = Path(__file__).with_name("_test_mc_totals_full.csv")
        try:
            totals = export_csv.export(path)
            self.assertEqual(list(np.round(np.percentile(totals, [50, 90]), 2)), [17.23, 20.56])
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
