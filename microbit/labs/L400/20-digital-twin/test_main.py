"""Lab 20 basics: the twin's model matches lab 17, calibration is sane, the fixture is reproducible."""
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import drift_eval  # noqa: E402
import twin_model  # noqa: E402

LAB17 = (HERE.parent / "17-edge-to-cloud" / "solution.py").read_text(encoding="utf-8")


class Model(unittest.TestCase):
    def test_timer_constants_match_lab_17(self):
        for name in ("TIMEOUT_MS", "MAX_TIMEOUT_MS", "MAX_TRIES", "SAMPLE_MS"):
            self.assertEqual(int(re.search(r"^%s = (\d+)" % name, LAB17, re.M).group(1)),
                             getattr(twin_model, name), name)

    def test_retry_share_is_about_the_loss(self):
        for loss in (0.05, 0.10, 0.30):
            self.assertAlmostEqual(twin_model.stats_for(loss)[0], loss, delta=0.01)

    def test_calibration_finds_each_links_loss(self):
        params = twin_model.calibrate(drift_eval.load_rows())
        true = {"n1": 0.05, "n2": 0.05, "n3": 0.10, "n4": 0.10, "n5": 0.15, "n6": 0.15}
        for dev, p in params.items():
            self.assertAlmostEqual(p["loss"], true[dev], delta=0.07, msg=dev)


class Fixture(unittest.TestCase):
    def test_first_150_s_regenerate_identically(self):
        import make_telemetry
        fresh = [r for r in make_telemetry.generate(duration_s=180) if r["t_sensor"] < 150000]
        saved = [r for rows in drift_eval.load_rows().values() for r in rows if r["t_sensor"] < 150000]
        key = lambda r: (r["dev"], r["seq"])                     # noqa: E731
        self.assertEqual([dict(r, t_store=r["t_store"]) for r in sorted(fresh, key=key)],
                         sorted(saved, key=key))


if __name__ == "__main__":
    unittest.main(verbosity=2)
