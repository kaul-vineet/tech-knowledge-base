"""buildTask check (lesson 16): a cached result must be reused only for the same data, code and parameters.

By default this checks solution/pipeline.py. To check your edited pipeline.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file 2 of 3 tests fail; after your fix all pass.
"""
import importlib.util
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("pipeline.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/pipeline.py")
spec = importlib.util.spec_from_file_location("pipeline_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


def caches(tmp):
    return [json.loads(x)["cache"] for x in (Path(tmp) / "prov.jsonl").read_text(encoding="utf-8").splitlines()]


class TestContentAddressedCache(unittest.TestCase):
    def test_new_release_is_recomputed(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, corrected = target.demo(Path(tmp))
            self.assertEqual(corrected["period_d"], 0.30112)
            self.assertEqual(caches(tmp)[-2:], ["miss", "miss"])

    def test_same_input_still_hits(self):
        with tempfile.TemporaryDirectory() as tmp:
            target.demo(Path(tmp))
            self.assertEqual(caches(tmp)[2:4], ["hit", "hit"])

    def test_parameter_change_reaches_downstream_steps(self):
        with tempfile.TemporaryDirectory() as tmp:
            p, src = target.Pipeline(tmp), Path(tmp) / "lightcurve.csv"
            shutil.copyfile(HERE / "data" / "lightcurve_v2.csv", src)
            p.run(src, window_nights=5)
            p.run(src, window_nights=1)
            self.assertEqual(caches(tmp), ["miss", "miss", "miss", "miss"])


if __name__ == "__main__":
    unittest.main()
