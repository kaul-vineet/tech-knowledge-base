"""The seams: where the quantum, distributed-systems and application-architecture parts meet."""
import unittest

import numpy as np

import shared  # noqa: F401
import loadtest
import results
import run_project
import scenarios
from _kb import sv
from canon import canonicalise, circuit_hash, to_sv


class RetriesShotAccounting(unittest.TestCase):
    """distributed-systems (at-least-once, leases) <-> quantum (shots are the statistical sample size)."""

    def test_redelivered_chunks_count_once(self):
        lab = shared.lease_lab()
        self.assertEqual(lab["lease_expiries"], 2)
        self.assertEqual(lab["returned"], lab["requested"])
        self.assertEqual([s.split(" ")[0] for _, _, s in lab["commits"]], ["accepted", "accepted", "REJECTED", "REJECTED"])

    def test_partial_failures_retry_only_the_failed_chunks(self):
        out = scenarios.partial_retry()
        self.assertEqual(out["returned"], 4000)
        self.assertEqual(len(out["commits"]), 4)                   # one accepted commit per chunk, nothing re-run

    def test_load_test_totals_exact(self):
        m = shared.load()
        self.assertEqual(m["shots_returned"], m["shots_requested"])


class CanonicalisationCacheKey(unittest.TestCase):
    """quantum (circuit equivalence) <-> application-architecture (cache key)."""

    def test_canonical_form_keeps_the_unitary(self):
        for texts in loadtest.CIRCUITS.values():
            for t in texts:
                n, ops, _ = canonicalise(t)
                self.assertTrue(sv.equal_up_to_global_phase(sv.unitary(n, to_sv(ops)), sv.unitary(*run_project._raw(t))))

    def test_inequivalent_circuits_never_share_a_key(self):
        a = "OPENQASM 3.0; qubit[2] q; h q[0]; cx q[0], q[1];"
        b = "OPENQASM 3.0; qubit[2] q; h q[1]; cx q[1], q[0];"          # same shape, different qubits: different state
        c = "OPENQASM 3.0; qubit[3] q; h q[0]; cx q[0], q[1];"          # an extra idle qubit changes the outcomes
        self.assertEqual(len({circuit_hash(a), circuit_hash(b), circuit_hash(c)}), 3)

    def test_variants_hit_the_cache(self):
        self.assertGreater(shared.load()["variant_hits"], 0)


class NoiseResultContract(unittest.TestCase):
    """quantum (noise, shot noise) <-> application-architecture (API contract): results carry uncertainty."""

    def test_every_result_meets_the_contract(self):
        self.assertEqual(shared.load()["contract_violations"], 0)

    def test_error_bars_are_honest(self):
        self.assertGreaterEqual(shared.load()["ci95_coverage"], 0.9)

    def test_missing_uncertainty_is_a_violation(self):
        r = results.build("x", {"00": 600, "11": 400}, 2, np.eye(4), "b", 1)
        r.pop("stderr")
        self.assertIn("missing stderr", results.violations(r, 1000))


class CalibrationDriftCache(unittest.TestCase):
    """quantum (calibration drift) <-> distributed-systems (cache invalidation)."""

    def test_hits_never_cross_versions(self):
        self.assertEqual(shared.load()["cache_crossings"], 0)

    def test_mid_job_drift_restarts_on_one_version(self):
        d = scenarios.drift_mid_job()
        self.assertEqual((d["restarts"], d["calibration_version"], d["returned"]), (1, 2, 4000))

    def test_versionless_key_crosses(self):
        self.assertGreater(shared.load("stale-cache")["cache_crossings"], 0)   # the guard detects the fault


if __name__ == "__main__":
    unittest.main()
