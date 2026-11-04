"""One test class per milestone. Run from the lab folder: python -m unittest discover -s tests -v"""
import unittest

import shared  # noqa: F401  (sys.path)
import backends as bk
import loadtest
import run_project
from canon import canonicalise, circuit_hash
from jobservice import Conflict, JobService
from ledger_loader import ledger_class


class M1Intake(unittest.TestCase):
    def test_variants_share_one_hash_and_families_differ(self):
        c = run_project.canon_check()
        self.assertTrue(c["one_hash_per_family"] and c["distinct_across_families"])

    def test_unsupported_statement_rejected_before_queueing(self):
        with self.assertRaises(ValueError):
            canonicalise("OPENQASM 3.0; qubit[1] q; rz(0.1) q[0];")

    def test_same_id_same_body_replays_different_body_conflicts(self):
        svc = JobService(bk.fleet(), ledger_class()())
        req = {"job_id": "a", "qasm": loadtest.CIRCUITS["bell"][0], "shots": 1000, "seed": 1, "min_fidelity": 0.8}
        first = svc.submit(req)
        self.assertIs(svc.submit(dict(req)), first)
        with self.assertRaises(Conflict):
            svc.submit({**req, "shots": 2000})
        self.assertEqual(len(svc.jobs), 1)


class M2BackendsAndScheduler(unittest.TestCase):
    def test_sampled_counts_match_the_noise_model(self):
        self.assertLessEqual(run_project.backend_probe()["tvd_sample_vs_exact"], 0.03)

    def test_scheduler_respects_the_fidelity_floor(self):
        self.assertEqual(shared.load()["below_floor"], 0)

    def test_floor_excludes_the_noisy_backend_for_ghz4(self):
        svc = JobService(bk.fleet(), ledger_class()())
        n, ops, _ = canonicalise(loadtest.CIRCUITS["ghz4"][0])
        self.assertNotEqual(svc.pick(n, ops, 0.75), "fast-noisy")      # fast-noisy estimate 0.6976 < 0.75


class M3ReliableExecution(unittest.TestCase):
    def test_all_jobs_complete_under_outage_slow_chunks_and_rejections(self):
        m = shared.load()
        self.assertEqual(m["completed"], m["jobs"])
        self.assertGreater(m["lease_expiries"], 0)
        self.assertGreaterEqual(m["breaker_opens"], 1)

    def test_bulkhead_never_exceeds_slots(self):
        m = shared.load()
        for name, slots in m["slots"].items():
            self.assertLessEqual(m["max_in_flight"][name], slots)


class M4ResultsWithErrorBars(unittest.TestCase):
    def test_contract_and_mitigation(self):
        p = run_project.backend_probe()
        self.assertEqual(shared.load()["contract_violations"], 0)
        self.assertLess(p["tvd_mitigated_vs_pre_readout"], p["tvd_raw_vs_pre_readout"])
        self.assertGreater(p["stderr_00_mitigated"], p["stderr_00_raw"])       # mitigation costs variance


class M5VersionedCache(unittest.TestCase):
    def test_hits_include_textual_variants_and_never_cross_versions(self):
        m = shared.load()
        self.assertGreater(m["variant_hits"], 0)
        self.assertEqual(m["cache_crossings"], 0)

    def test_key_changes_with_calibration_version(self):
        from cachekeys import cache_key
        b, text = bk.fleet()[1], loadtest.CIRCUITS["bell"][0]
        before = cache_key(text, circuit_hash(text), b, 1000, 1)
        b.recalibrate(b.cal)
        self.assertNotEqual(before, cache_key(text, circuit_hash(text), b, 1000, 1))


if __name__ == "__main__":
    unittest.main()
