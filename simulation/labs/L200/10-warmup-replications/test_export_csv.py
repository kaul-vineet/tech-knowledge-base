import csv
import unittest
from pathlib import Path

import export_csv


class TestExportCsv(unittest.TestCase):
    def test_two_scenarios_reproduce_lab_means(self):
        path = Path(__file__).with_name("_test_replications.csv")
        try:
            export_csv.export(path)
            with path.open(encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 80)
            for name, expected in (("delete 0", 5.59), ("delete 169", 3.71)):
                means = [float(r["mean_wait_min"]) for r in rows if r["scenario"] == name]
                self.assertEqual(len(means), 40)
                self.assertAlmostEqual(sum(means) / 40, expected, places=2)
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
