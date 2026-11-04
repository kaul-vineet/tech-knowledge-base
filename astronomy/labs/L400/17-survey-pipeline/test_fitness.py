"""Fitness function (lesson 17, ADR 0001): keeps "vectorised batches of 16 frames in one process (option C)" true.

Fails the build if the pipeline stops meeting the brief: completeness >= 0.95 (peak SNR >= 10), purity >= 0.98,
the SAME catalogue from options A, B and C, and option C >= 50 frames/s on this runner (best of 3 runs - wall-clock
bound kept generous; the sandbox measured ~259 frames/s on 1 CPU).
Default target: solution/survey.py; BUILD_TARGET=mine checks your survey.py (the shipped file fails).
"""
import importlib.util
import os
import unittest
from pathlib import Path

import survey_sim as sim

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("survey.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/survey.py")
spec = importlib.util.spec_from_file_location("survey_fitness", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestSurveyFitness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raws, cls.bias, cls.flat, cls.truth = sim.night()

    def test_detection_quality(self):
        rows, _, _ = target.run("A", self.raws, self.bias, self.flat)
        comp, pur = target.score(rows, self.truth)
        self.assertGreaterEqual(comp, 0.95)
        self.assertGreaterEqual(pur, 0.98)

    def test_same_catalogue_from_every_option(self):
        sums = {o: target.checksum(target.run(o, self.raws, self.bias, self.flat, workers=2)[0]) for o in "ABC"}
        self.assertEqual(len(set(sums.values())), 1, sums)

    def test_throughput_of_the_chosen_option(self):
        best = max(len(self.raws) / target.run("C", self.raws, self.bias, self.flat)[2] for _ in range(3))
        self.assertGreaterEqual(best, 50.0)


if __name__ == "__main__":
    unittest.main()
