"""buildTask check (lesson 21): check_card() must test each claim against the evidence, not just the headings.

By default this checks solution/governance.py. To check your edited governance.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file 1 of 2 tests fails (the honest card passes either way); after your fix both pass.
"""
import importlib.util
import json
import os
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("governance.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/governance.py")
spec = importlib.util.spec_from_file_location("governance_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)
# Fixed evidence (what governance.py measured), so this test runs in milliseconds
EVIDENCE = {"verification": {"tests_run": 7, "failures": 0}, "envelope_rho_max": 0.85, "max_rel_error_in_envelope": 0.055,
            "most_influential": "mu", "code_sha256": target.sha256(target.MODEL_FILE),
            "data_sha256": target.sha256(target.DATA_FILE)}


def card(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


class TestClaimChecks(unittest.TestCase):
    def test_honest_card_has_no_findings(self):
        self.assertEqual(target.check_card(card("model_card.json"), EVIDENCE), [])

    def test_every_overclaim_in_the_draft_is_found(self):
        findings = " | ".join(target.check_card(card("cards/draft_overclaiming.json"), EVIDENCE))
        for word in ("envelope", "error", "influential", "code_sha256"):
            with self.subTest(claim=word):
                self.assertIn(word, findings)


if __name__ == "__main__":
    unittest.main()
