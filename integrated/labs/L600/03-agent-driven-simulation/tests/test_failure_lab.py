"""Failure lab: 'significant improvement' from 3 replications. Reproduce with --inject few-reps; the fix sizes n."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _fixture  # noqa: E402
import unittest  # noqa: E402

import contextlib  # noqa: E402
import io  # noqa: E402
import shutil  # noqa: E402

import run_project  # noqa: E402


def significance_rows(rows):
    return [r for r in rows if "significant improvement" in r["sentence"]]


class TestFailureLab(unittest.TestCase):
    def test_fault_reproduces_and_the_checker_rejects_the_claim(self):
        reg, _, _, rows, published = _fixture.session("few-reps")
        row = significance_rows(rows)[0]
        self.assertIn("with 3 replications", row["sentence"])
        self.assertFalse(row["ok"])
        self.assertIn("claims significance", row["reason"])
        self.assertIn("inconclusive", published)

    def test_fixed_pipeline_supports_the_claim(self):
        rows = _fixture.session()[3]
        row = significance_rows(rows)[0]
        self.assertIn("with 55 replications", row["sentence"])
        self.assertTrue(row["ok"], row["reason"])

    def test_scorecard_fails_with_the_fault_and_passes_without(self):
        out = _fixture.LAB / "out" / "test-failure-lab"
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                code = run_project.main(["--inject", "few-reps", "--out", str(out)])
            self.assertEqual(code, 1)
        finally:
            shutil.rmtree(out, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
