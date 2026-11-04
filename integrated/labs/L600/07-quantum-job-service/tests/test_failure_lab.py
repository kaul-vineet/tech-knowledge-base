"""Failure lab: a lease expiry during a slow backend -> duplicate execution -> merged counts exceed the request.

The shipped ledger (fault 'lease-expiry') reproduces the bug; the reference ledger fixes it. Deterministic (fake clock):
the scenario is repeated 3 times and must give identical results each time.
"""
import unittest

import shared
import run_project
import scenarios


class FailureLab(unittest.TestCase):
    def test_fault_reproduces(self):
        bad = shared.lease_lab("lease-expiry")
        self.assertEqual((bad["requested"], bad["returned"]), (2000, 4000))
        self.assertGreater(shared.load("lease-expiry")["shots_returned"], shared.load("lease-expiry")["shots_requested"])

    def test_fix_gives_exact_totals_three_times(self):
        runs = [scenarios.lease_expiry() for _ in range(3)]
        for r in runs:
            self.assertEqual(r["returned"], r["requested"])
        self.assertEqual(len({str(r["commits"]) for r in runs}), 1)

    def test_scorecard_fails_with_the_fault(self):
        rows = run_project.lines({**self._base(), "load": shared.load("lease-expiry"), "lab": shared.lease_lab("lease-expiry")})
        failed = {name for kind, name, ok, _ in rows if not ok}
        self.assertIn("retries <-> shot accounting", failed)
        self.assertIn("shots returned == shots requested for 100% of jobs", failed)

    def _base(self):
        return {"drift": scenarios.drift_mid_job(), "partial": scenarios.partial_retry(),
                "canon": run_project.canon_check(), "probe": run_project.backend_probe()}


if __name__ == "__main__":
    unittest.main()
