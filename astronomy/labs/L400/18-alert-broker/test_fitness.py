"""Fitness function (lesson 18, ADR 0001): keeps "PSF-matched differences + broker filter + association" true.

Option C must publish <= 6 alerts per night with a real fraction >= 0.8, alert the supernova as a transient on
every night from night 3, never call the known variable V1 a transient, classify >= 80% of asteroid detections
as moving, and produce schema-valid packets only.
Default target: solution/alerts.py; BUILD_TARGET=mine checks your alerts.py (the shipped file fails).
"""
import importlib.util
import os
import unittest
from pathlib import Path

import numpy as np

import alert_sim as sim

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("alerts.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/alerts.py")
spec = importlib.util.spec_from_file_location("alerts_fitness", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestBrokerFitness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exposures = sim.nights()
        cls.out = target.run("C", cls.exposures)
        cls.summary = target.summary("C", cls.out, cls.exposures)

    def near(self, x, y, r=2.0):
        return [(n, p) for n, _, p in self.out if np.hypot(p["candidate"]["x"] - x, p["candidate"]["y"] - y) < r]

    def test_alert_volume_and_purity(self):
        self.assertLessEqual(self.summary["alerts_per_night"], 6)
        self.assertGreaterEqual(self.summary["real_fraction"], 0.8)
        self.assertEqual(self.summary["schema_errors"], 0)

    def test_supernova_every_night_from_3(self):
        nights = {n for n, p in self.near(*sim.SN_POS) if p["class"] == "transient"}
        self.assertEqual(nights, {3, 4, 5, 6, 7})

    def test_known_variable_is_never_a_transient(self):
        _, vx, vy = sim.known_variables()[0]
        self.assertTrue(all(p["class"] == "known_variable" for _, p in self.near(vx, vy)))

    def test_asteroid_is_moving(self):
        hits = [p["class"] for e in self.exposures for n, _, p in self.out if n == e["night"]
                and np.hypot(p["candidate"]["x"] - e["truth_asteroid"][0], p["candidate"]["y"] - e["truth_asteroid"][1]) < 2]
        self.assertGreaterEqual(hits.count("moving") / max(len(hits), 1), 0.8)


if __name__ == "__main__":
    unittest.main()
