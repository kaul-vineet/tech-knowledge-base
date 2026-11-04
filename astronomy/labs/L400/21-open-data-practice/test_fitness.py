"""Fitness function (lesson 21, ADR 0001): the release gate. check() must return [] for the release we publish,
and must catch each of the 6 seeded defects (manifest, CFF key, licence, credit, VOTable row, unit).
Default target: solution/release.py; BUILD_TARGET=mine checks your release.py (the shipped file fails).
"""
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

import defects

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("release.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/release.py")
spec = importlib.util.spec_from_file_location("release_fitness", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestReleaseGate(unittest.TestCase):
    def test_published_release_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(target.check(target.build(Path(tmp) / "release")), [])

    def test_every_seeded_defect_is_caught(self):
        self.assertTrue(all(b for _, b, _ in defects.caught().values()))


if __name__ == "__main__":
    unittest.main()
