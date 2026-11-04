"""Milestone tests for the capstone (M1-M6). The full search runs once per test process (about 30 s)."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

import agent_explain
import make_data
import pipeline
import run_capstone

HERE = Path(__file__).resolve().parent


def setUpModule():
    global RESULTS, PROV, TRUTH
    RESULTS, PROV = run_capstone.analyse_all()
    TRUTH = json.loads((run_capstone.DATA / "truth.json").read_text(encoding="utf-8"))


class M1Data(unittest.TestCase):
    def test_data_are_reproducible_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_data.write(tmp)
            self.assertEqual(hashlib.sha256((Path(tmp) / "S01.csv").read_bytes()).hexdigest()[:12], "3a31a29c1689")

    def test_detrended_noise_matches_injected_noise(self):
        for s, v in TRUTH.items():
            if v["kind"] in ("quiet", "ramp"):
                with self.subTest(star=s):
                    self.assertAlmostEqual(RESULTS[s]["rms_ppm"] / v["noise_ppm"], 1.0, delta=0.15)


class M2Search(unittest.TestCase):
    def test_periods_within_0p1_percent(self):
        for s in ("S01", "S02", "S03", "S04", "S05"):
            with self.subTest(star=s):
                self.assertLess(abs(RESULTS[s]["period_d"] / TRUTH[s]["period_d"] - 1), 0.001)

    def test_box_injection_recovered(self):
        t = make_data.T
        f = 1.0 + np.random.default_rng(1).normal(0, 3e-4, t.size)
        f[np.abs((t - 0.5 + 2.5) % 5.0 - 2.5) * 24 < 1.25] -= 0.002
        _, c = pipeline.bls(t, f)
        self.assertAlmostEqual(c["period_d"], 5.0, delta=0.005)


class M3Vetting(unittest.TestCase):
    def test_planets_pass_everything_else_rejected(self):
        found = sorted(s for s, r in RESULTS.items() if r["verdict"] == "planet_candidate")
        self.assertEqual(found, ["S01", "S02", "S03"])
        self.assertIn("secondary eclipse", RESULTS["S04"]["reasons"][0])
        self.assertIn("odd/even", RESULTS["S05"]["reasons"][0])


class M4Fit(unittest.TestCase):
    def test_depth_within_three_sigma_and_sampler_healthy(self):
        for s in ("S01", "S02", "S03"):
            fit = RESULTS[s]["fit"]
            with self.subTest(star=s):
                self.assertLessEqual(abs(fit["depth_ppm"] - TRUTH[s]["depth"] * 1e6), 3 * fit["depth_err_ppm"])
                self.assertTrue(0.2 <= fit["acceptance"] <= 0.5)


class M5Provenance(unittest.TestCase):
    def test_every_input_hashed_with_parameters(self):
        self.assertEqual([p["used"] for p in PROV], [f"S{i:02d}.csv" for i in range(1, 13)])
        self.assertEqual(PROV[0]["params"], {"window_d": 0.75, "snr_min": 10.0, "sde_min": 7.0})


class M6Agent(unittest.TestCase):
    def test_gate(self):
        facts = {"star": "S04", "period_d": 2.8454, "depth_ppm": 17900, "verdict": "rejected", "reasons": "x"}
        self.assertEqual(agent_explain.check("S04 repeats every 2.8454 days; it is a planet.", facts), ([], True))
        self.assertEqual(agent_explain.check("S04 repeats every 2.8454 days at 17900 ppm.", facts), ([], False))
        self.assertEqual(agent_explain.check("About 1.8 Earth radii.", facts), (["1.8"], False))

    def test_fake_model_never_changes_a_verdict(self):
        sys.path.insert(0, str(HERE.parent / "_agent"))
        import fake_model_server
        server, url = fake_model_server.start_in_thread()
        try:
            r = RESULTS["S05"]
            e = agent_explain.explain({"star": "S05", "period_d": r["period_d"], "depth_ppm": r["depth_ppm"],
                                       "verdict": r["verdict"], "reasons": r["reasons"][0]}, base_url=url)
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual((e["overclaim"], e["unverified"], e["publish"]), (True, ["1.8"], False))
        self.assertEqual(RESULTS["S05"]["verdict"], "rejected")


if __name__ == "__main__":
    unittest.main()
