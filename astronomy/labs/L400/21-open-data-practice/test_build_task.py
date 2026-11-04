"""buildTask check (lesson 21): the release licence must keep every input's restrictions.

By default this checks solution/release.py. To check your edited release.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v      (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file 2 of 3 build-task tests fail; after your fix all pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("release.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/release.py")
spec = importlib.util.spec_from_file_location("release_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


def inp(family):
    return {"name": family.lower(), "licence": "x", "family": family, "credit": "c"}


class TestLicencePropagation(unittest.TestCase):
    def test_noncommercial_input_keeps_nc(self):
        self.assertEqual(target.release_licence([inp("BY"), inp("BY-NC"), inp("PD")]), "CC-BY-NC-4.0")

    def test_permissive_inputs_stay_by(self):
        self.assertEqual(target.release_licence([inp("BY"), inp("PD")]), "CC-BY-4.0")

    def test_conflict_goes_to_a_human(self):
        with self.assertRaises(ValueError):
            target.release_licence([inp("BY-NC"), inp("BY-SA")])


if __name__ == "__main__":
    unittest.main()
