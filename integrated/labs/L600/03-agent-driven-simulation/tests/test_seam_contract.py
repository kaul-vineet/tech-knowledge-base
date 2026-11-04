"""Seam agent <-> tool schema: out-of-range or invented arguments are rejected before anything runs or is charged."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _fixture  # noqa: E402
import unittest  # noqa: E402

import contract  # noqa: E402
import pipeline  # noqa: E402
import registry  # noqa: E402

A, B = _fixture.A, _fixture.B
BAD = {
    "lam above schema maximum": {"baseline": {"lam": 0.97, "mu": 1.0}, "candidate": B},
    "mu below schema minimum": {"baseline": A, "candidate": {"lam": 0.5, "mu": 0.5}},
    "utilisation outside envelope": {"baseline": A, "candidate": {"lam": 0.9, "mu": 0.95}},
    "invented field": {"baseline": {**A, "priority": "high"}, "candidate": B},
    "string instead of number": {"baseline": {"lam": "0.8", "mu": 1.0}, "candidate": B},
    "boolean replications": {"baseline": A, "candidate": B, "replications": True},
    "too many customers": {"baseline": {**A, "customers": 10**6}, "candidate": B},
    "missing candidate": {"baseline": A},
}


class TestContractSeam(unittest.TestCase):
    def test_every_bad_proposal_is_rejected_with_a_reason(self):
        for label, args in BAD.items():
            with self.subTest(label):
                self.assertTrue(contract.validate("run_experiment", args))

    def test_rejected_proposals_cost_nothing_and_leave_no_runs(self):
        pl = pipeline.Pipeline(registry.Registry(), pipeline.SimBudget(10**6))
        for args in BAD.values():
            self.assertEqual(pl.submit("run_experiment", args)["status"], "rejected")
        self.assertEqual(pl.submit("delete_registry", {})["status"], "rejected")
        self.assertEqual((pl.registry.records, pl.budget.spent), ([], 0))

    def test_valid_proposal_passes(self):
        self.assertEqual(contract.validate("run_experiment", {"baseline": A, "candidate": B, "replications": 3}), [])

    def test_without_the_gate_the_session_runs_outside_the_envelope(self):
        _, pl, *_ = _fixture.session("no-contract")
        ran = [j for j in pl.jobs if "RAN" in j["states"] and j["args"]["baseline"]["lam"] == 0.97]
        self.assertEqual(len(ran), 1)


if __name__ == "__main__":
    unittest.main()
