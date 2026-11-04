"""Unit tests + fault reproduction for lesson 13 (numpy only; the ccdproc equivalence test is skipped locally)."""
import tempfile
import unittest
from pathlib import Path

import numpy as np

import calibrate
import camera
from fitsmini import write_fits


class TestMasters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = camera.frames()
        cls.bias, cls.dark, cls.flat = calibrate.masters(cls.f)

    def test_master_bias_and_dark_levels(self):
        self.assertAlmostEqual(float(np.median(self.bias)), camera.BIAS, delta=0.5)
        self.assertAlmostEqual(float(np.median(self.dark)), camera.DARK_E_S * camera.EXPTIME / camera.GAIN, delta=0.2)
        self.assertGreater(float(self.dark.max()), 190)  # hot pixels: 5 e-/s x 60 s / 1.5 = 200 ADU

    def test_sigma_clip_rejects_a_cosmic_ray(self):
        stack = np.full((10, 4, 4), 100.0) + np.random.default_rng(1).normal(0, 1, (10, 4, 4))
        stack[3, 2, 2] = 20000.0
        self.assertAlmostEqual(float(calibrate.sigma_clip_mean(stack)[2, 2]), 100.0, delta=2.0)

    def test_cosmic_cleaner_keeps_the_star_and_removes_the_hit(self):
        img = 100.0 + camera.star_image(30.0, 30.0, 100_000.0) / camera.GAIN
        img[10, 10] += 5000.0
        clean, n = calibrate.clean_cosmics(img, 5.0)
        self.assertEqual(n, 1)
        self.assertAlmostEqual(float(clean[30, 30]), float(img[30, 30]), places=6)

    def test_photometry_recovers_a_noiseless_star(self):
        img = 50.0 + camera.star_image(30.3, 31.7, 10_000.0)
        self.assertAlmostEqual(calibrate.photometry(img, 30.3, 31.7)[0] / 10_000.0, 1.0, delta=0.01)


class TestFits(unittest.TestCase):
    def test_header_blocks_and_round_trip(self):
        data = np.arange(12, dtype=float).reshape(3, 4)
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x.fits"
            write_fits(p, data)
            raw = p.read_bytes()
        self.assertEqual(len(raw) % 2880, 0)
        header = raw[:2880].decode("ascii")
        self.assertTrue(header.startswith("SIMPLE  =                    T"))
        self.assertIn("NAXIS1  =                    4", header)
        back = np.frombuffer(raw[2880:2880 + 48], dtype=">f4").reshape(3, 4)
        np.testing.assert_array_equal(back, data)


class TestFailureLab(unittest.TestCase):
    """Shipped masters(): the flat keeps its 1000 ADU bias pedestal, so normalising flattens the response."""

    def test_shipped_flat_creates_fake_variability(self):
        rel, s, flat = calibrate.run(log_path=None)
        self.assertTrue(s["variable"])
        self.assertAlmostEqual(s["robust_rms_percent"], 0.899, delta=0.0005)
        self.assertAlmostEqual(float(flat.min()), 0.8527, places=4)

    def test_log_lines_are_json(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            calibrate.run(log_path=Path(tmp) / "log.jsonl")
            lines = [json.loads(x) for x in (Path(tmp) / "log.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(lines), 3 + camera.N_FRAMES + 1)
        self.assertEqual(lines[3 + 17]["cosmics_cleaned"], 4)


class TestCcdprocEquivalent(unittest.TestCase):
    def test_ccdproc_light_curve_is_also_flat(self):
        try:
            import calibrate_ccdproc
        except ImportError:
            self.skipTest("astropy/ccdproc not installed (pending-ci)")
        _, rms = calibrate_ccdproc.reduce()
        self.assertLess(rms, 0.6)


if __name__ == "__main__":
    unittest.main()
