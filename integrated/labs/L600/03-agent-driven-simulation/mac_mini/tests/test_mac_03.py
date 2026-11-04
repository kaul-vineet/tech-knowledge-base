"""Project 03 Mac mini scripts, tested here with the fake model and tiny sizes (scratch folders next to this file)."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

MAC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MAC))
import _lab  # noqa: E402,F401
import compare_models  # noqa: E402
import export_rejections  # noqa: E402
import overnight_sweep  # noqa: E402


class Scratch(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="scratch-", dir=Path(__file__).parent))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def rows(self, name):
        return [json.loads(x) for x in (self.tmp / name).read_text(encoding="utf-8").splitlines()]


class CompareModelsTest(Scratch):
    def test_fake_model_record(self):
        self.assertEqual(compare_models.main(["--here", "--out", str(self.tmp)]), 0)
        (r,) = self.rows("03-compare-models.jsonl")
        self.assertEqual(r["model"], "fake-model")
        self.assertEqual(r["contract_rejected"], 1)          # lam 0.97: outside the schema maximum 0.95
        self.assertEqual(r["budget_rejected"], 1)            # morris screening no longer fits the budget
        self.assertGreaterEqual(r["claims_dropped"], 1)      # the uncited textbook number for lam 0.97
        self.assertEqual(r["published_traced"], r["numbers_found"])
        self.assertTrue(r["budget_respected"])
        self.assertTrue(any("0.97" in e for p in r["rejected_proposals"] for e in p["errors"]))

    def test_unreachable_server_is_an_error_not_a_crash(self):
        old = os.environ.get("LOCAL_MODEL_URL")
        os.environ["LOCAL_MODEL_URL"] = "http://127.0.0.1:9/v1"  # discard port: connection refused
        try:
            code = compare_models.main(["--models", "nobody:1b", "--out", str(self.tmp)])
        finally:
            os.environ.pop("LOCAL_MODEL_URL") if old is None else os.environ.__setitem__("LOCAL_MODEL_URL", old)
        self.assertEqual(code, 1)
        (r,) = self.rows("03-compare-models.jsonl")
        self.assertIn("error", r)

    def test_profile_sizes_the_model_list(self):
        self.assertEqual(compare_models.models_from_profile(16), ["qwen2.5:3b", "qwen2.5:7b", "qwen2.5:14b"])
        self.assertIn("qwen2.5:32b", compare_models.models_from_profile(64))


class SweepTest(unittest.TestCase):
    def test_same_bits_for_any_worker_count(self):
        one, v1 = overnight_sweep.coverage([0.8], 2, 3, 1, customers=2500)
        two, v2 = overnight_sweep.coverage([0.8], 2, 3, 2, customers=2500)
        self.assertEqual(overnight_sweep.digest(v1), overnight_sweep.digest(v2))
        self.assertEqual(one, two)

    def test_coverage_row_maths(self):
        rows, values = overnight_sweep.coverage([0.5], 3, 4, 1, customers=2500)
        self.assertEqual(len(values), 12)
        self.assertEqual(rows[0]["formula"], 1.0)  # Wq = 0.5 / (1 x 0.5)
        self.assertIn(rows[0]["coverage"], (0.0, 0.3333, 0.6667, 1.0))


class ExportTest(unittest.TestCase):
    def test_labels_are_recomputed_and_budget_refusals_skipped(self):
        row = {"model": "m", "rejected_proposals": [
            {"tool": "run_experiment", "args": {"baseline": {"lam": 0.93, "mu": 1.0}, "candidate": {"lam": 0.93, "mu": 1.1}},
             "errors": ["(logged text is ignored)"]},
            {"tool": "run_screening", "args": {"method": "morris", "size": 10}, "errors": ["budget: too big"]},
            {"tool": "run_screening", "args": None, "errors": ["arguments are not valid JSON (x)"]}]}
        ex = export_rejections.examples([row])
        self.assertEqual(len(ex), 2)
        self.assertTrue(ex[0]["messages"][2]["content"].startswith("REJECTED"))
        self.assertIn("0.93", ex[0]["messages"][2]["content"])
        self.assertEqual(ex[1]["messages"][2]["content"], "REJECTED: arguments are not a JSON object")
        self.assertEqual([m["role"] for m in ex[0]["messages"]], ["system", "user", "assistant"])

    def test_split_is_deterministic(self):
        items = [{"messages": [{"role": "user", "content": str(i)}]} for i in range(10)]
        self.assertEqual(export_rejections.split(items), export_rejections.split(list(reversed(items))))
        train, valid = export_rejections.split(items)
        self.assertEqual((len(train), len(valid)), (8, 2))


if __name__ == "__main__":
    unittest.main()
