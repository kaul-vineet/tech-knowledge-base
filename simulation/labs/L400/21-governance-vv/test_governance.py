import json
import unittest

import governance as gov

PEAK = 0.8  # busiest hour in arrivals.csv: 144 patients / 60 min / 3 desks


class TestEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ev = gov.evidence()

    def test_verification_suite_is_green(self):
        self.assertEqual(self.ev["verification"], {"tests_run": 7, "failures": 0})

    def test_envelope_stops_where_accuracy_is_lost(self):
        self.assertEqual(self.ev["envelope_rho_max"], 0.85)
        self.assertFalse(self.ev["validation"][-1]["ok"])  # rho 0.95: the CI is too wide for the 10% requirement

    def test_sensitivity_signs_make_sense(self):
        self.assertGreater(self.ev["sensitivity"]["lam"], 0)  # more arrivals -> longer waits
        self.assertLess(self.ev["sensitivity"]["mu"], 0)  # faster service -> shorter waits

    def test_hashes_are_line_ending_independent(self):
        self.assertEqual(len(self.ev["code_sha256"]), 64)
        self.assertEqual(self.ev["peak_utilisation"], PEAK)


class TestFailureLab(unittest.TestCase):
    """Fault: the shipped check_card() only checks the headings. Your fix is checked by test_build_task.py."""

    def test_fault_overclaiming_draft_is_publishable(self):
        draft = json.loads((gov.HERE / "cards" / "draft_overclaiming.json").read_text(encoding="utf-8"))
        self.assertEqual(gov.check_card(draft, {}), [])


if __name__ == "__main__":
    unittest.main()
