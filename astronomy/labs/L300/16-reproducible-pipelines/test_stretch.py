"""Stretch check (lesson 16): lineage() traces the final result back through detrend to the v2 input file.

Checks solution/lineage.py; BUILD_TARGET=mine checks lineage.py in this folder (your copy).
"""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("lineage.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/lineage.py")
spec = importlib.util.spec_from_file_location("lineage_under_test", TARGET)
lin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lin)
spec2 = importlib.util.spec_from_file_location("pipeline_fixed", HERE / "solution" / "pipeline.py")
pipe = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(pipe)


class TestLineage(unittest.TestCase):
    def test_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipe.demo(Path(tmp))
            lines = (Path(tmp) / "prov.jsonl").read_text(encoding="utf-8").splitlines()
        chain = lin.lineage(lines, json.loads(lines[-1])["generated_sha256"])
        self.assertEqual([c["activity"] for c in chain], ["best_period", "detrend"])
        self.assertEqual(chain[1]["params"], {"window_nights": 5})
        self.assertEqual(chain[1]["input_file_sha256"], "6141395bece9")


if __name__ == "__main__":
    unittest.main()
