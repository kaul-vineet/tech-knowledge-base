"""Seam agent claims <-> computed statistics: every sentence is checked against the cited experiment's facts."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _fixture  # noqa: E402
import unittest  # noqa: E402

import claims  # noqa: E402


class TestClaimSeam(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg = _fixture.session()[0]
        cls.exp, cls.f = _fixture.ab_facts(cls.reg)

    def check(self, sentence):
        return claims.check_sentence(sentence, self.reg)

    def test_correct_sentence_passes(self):
        s = f"Mean wait fell from {self.f['baseline_mean']:.2f} to {self.f['candidate_mean']:.2f} min, a significant decrease [{self.exp}]."
        self.assertTrue(self.check(s)["ok"])

    def test_uncited_number_is_rejected(self):
        self.assertIn("untraced", self.check("The wait drops to 3.14 min.")["reason"])

    def test_unknown_experiment_is_rejected(self):
        self.assertIn("not in the registry", self.check("Wait 3.14 min [exp-deadbeef].")["reason"])

    def test_overstated_percentage_is_rejected(self):
        r = self.check(f"Waits fell by 40%, a significant improvement [{self.exp}].")
        self.assertFalse(r["ok"])
        self.assertIn("40", r["reason"])

    def test_more_precision_than_computed_is_rejected(self):
        self.assertFalse(self.check(f"Mean wait {self.f['baseline_mean'] + 0.004:.3f} min [{self.exp}].")["ok"])

    def test_wrong_direction_and_false_negation_are_rejected(self):
        self.assertFalse(self.check(f"A significant increase in waits [{self.exp}].")["ok"])
        self.assertFalse(self.check(f"The change is not significant [{self.exp}].")["ok"])

    def test_direction_without_significance_qualifier_is_rejected(self):
        self.assertIn("direction", self.check(f"Faster service cut waits [{self.exp}].")["reason"])

    def test_code_written_line_passes_its_own_check(self):
        self.assertTrue(self.check(claims.code_line(self.exp, self.reg))["ok"])


if __name__ == "__main__":
    unittest.main()
