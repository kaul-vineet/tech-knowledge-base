"""Unit tests + fault reproduction for lesson 16 (numpy only; the joblib test is skipped locally)."""
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np

import make_data
import pipeline
from periodogram import lomb_scargle

HERE = Path(__file__).resolve().parent


class TestPieces(unittest.TestCase):
    def test_committed_data_is_the_seeded_release(self):
        t, tel, mag = make_data.light_curve()
        with tempfile.TemporaryDirectory() as tmp:
            make_data.write(Path(tmp) / "v2.csv", t, tel, mag)
            self.assertEqual((Path(tmp) / "v2.csv").read_bytes(), (HERE / "data" / "lightcurve_v2.csv").read_bytes())
        digest = hashlib.sha256((HERE / "data" / "lightcurve_v2.csv").read_bytes()).hexdigest()
        self.assertTrue(digest.startswith("6141395bece9"))

    def test_lomb_scargle_finds_a_pure_sinusoid(self):
        t = np.sort(np.random.default_rng(0).uniform(0, 20, 200))
        f = np.linspace(0.1, 5, 5000)
        p = lomb_scargle(t, np.sin(2 * np.pi * 1.7 * t), f)
        self.assertAlmostEqual(float(f[p.argmax()]), 1.7, delta=0.002)
        self.assertGreater(float(p.max()), 0.99)

    def test_v2_gives_the_true_period_and_v1_an_alias(self):
        v1 = pipeline.best_period(pipeline.detrend(pipeline.load(HERE / "data" / "lightcurve_v1.csv")))
        v2 = pipeline.best_period(pipeline.detrend(pipeline.load(HERE / "data" / "lightcurve_v2.csv")))
        self.assertEqual((v1["period_d"], v2["period_d"]), (0.43049, 0.30112))


class TestFailureLab(unittest.TestCase):
    """Shipped cache_key() = step name + FILE NAME + params: the corrected v2 release hits the v1 cache."""

    def test_stale_cache_is_silently_reused(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, again, corrected = pipeline.demo(Path(tmp))
            prov = [json.loads(x) for x in (Path(tmp) / "prov.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(corrected["period_d"], 0.43049)  # stale v1 answer for v2 data
        self.assertEqual([r["cache"] for r in prov], ["miss", "miss", "hit", "hit", "hit", "hit"])
        self.assertNotEqual(prov[0]["used"]["sha256"], prov[4]["used"]["sha256"])  # the log saw the new file


class TestJoblibEquivalent(unittest.TestCase):
    def test_joblib_path_key_is_stale_data_key_is_not(self):
        try:
            import cache_joblib
        except ImportError:
            self.skipTest("joblib not installed (pending-ci)")
        self.assertEqual(cache_joblib.compare(), (0.43049, 0.30112))


if __name__ == "__main__":
    unittest.main()
