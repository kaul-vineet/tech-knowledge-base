"""Unit tests + fault reproduction for lesson 17 (numpy + stdlib)."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

import numpy as np

import survey
import survey_sim as sim

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("survey_fixed", HERE / "solution" / "survey.py")
fixed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixed)


class TestStages(unittest.TestCase):
    def test_mesh_background_follows_the_moonlight_gradient(self):
        bkg = fixed.background(np.stack([sim.SKY, sim.SKY]))
        self.assertLess(float(np.abs(bkg[0, :, 16:112] - sim.SKY[:, 16:112]).max()), 1e-6)  # linear sky: exact inside

    def test_detect_one_star_with_subpixel_centroid(self):
        img = 100.0 + 5000 * np.exp(-((sim.XX - 40.3) ** 2 + (sim.YY - 70.6) ** 2) / (2 * 1.3 ** 2))
        img += np.random.default_rng(0).normal(0, 3, img.shape)
        rows = survey.detect(img[None], np.full((1,) + img.shape, 100.0))
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0][1], 40.3, delta=0.05)
        self.assertAlmostEqual(rows[0][2], 70.6, delta=0.05)

    def test_metrics_log_is_json_lines(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            fixed.main(workers=1, log=Path(tmp) / "m.jsonl")
            lines = [json.loads(x) for x in (Path(tmp) / "m.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(lines), 48 + 48 + 3)  # A: one per frame, B: one per frame, C: one per batch of 16
        self.assertEqual({"option", "unit", "frames", "ingest_s", "calibrate_s", "detect_s"}, set(lines[0]))


class TestFailureLab(unittest.TestCase):
    """Shipped background(): one median per frame. The gradient inflates the robust rms, the 5-sigma threshold
    rises, and 83% of detectable stars are lost (purity stays perfect, so nothing looks wrong)."""

    def test_global_background_loses_most_stars(self):
        raws, bias, flat, truth = sim.night()
        rows, _, _ = survey.run("A", raws, bias, flat)
        self.assertEqual(len(rows), 172)
        self.assertEqual(survey.score(rows, truth), (0.1745, 1.0))


if __name__ == "__main__":
    unittest.main()
