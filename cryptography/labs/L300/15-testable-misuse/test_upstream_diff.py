"""upstream_diff.py against a fake upstream folder (offline): built from the vendored subsets, then one value is changed."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import upstream_diff as ud


def fake_upstream(folder: Path, edit=None) -> None:
    for ours, (theirs, _) in ud.PAIRS.items():
        doc = json.loads((ud.VECTORS / ours).read_text(encoding="utf-8"))
        if edit and ours == edit:
            doc["testGroups"][0]["tests"][0]["tag" if "gcm" in ours else "sig"] = "00" * 16
        (folder / theirs).write_text(json.dumps(doc), encoding="utf-8")


class TestUpstreamDiff(unittest.TestCase):
    def run_main(self, folder: Path) -> tuple:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ud.main(["--upstream", str(folder), "--ref", "test"])
        return code, out.getvalue()

    def test_identical_upstream_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_upstream(Path(tmp))
            code, out = self.run_main(Path(tmp))
        self.assertEqual(code, 0)
        self.assertIn("5/5 vendored cases found verbatim", out)
        self.assertIn("11/11 vendored cases found verbatim", out)

    def test_changed_value_is_reported_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_upstream(Path(tmp), edit="aes_gcm_subset.json")
            code, out = self.run_main(Path(tmp))
        self.assertEqual(code, 1)
        self.assertIn("tcId 1: MISSING upstream", out)


if __name__ == "__main__":
    unittest.main()
