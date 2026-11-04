import hmac
import json
import unittest

import nonce_guard as ng
import timing_demo as td
import wycheproof_check as wc


class TestHarness(unittest.TestCase):
    def test_vendored_files_have_wycheproof_shape(self):
        gcm, ed = wc.load("aes_gcm_subset.json"), wc.load("ed25519_subset.json")
        self.assertEqual(gcm["testGroups"][0]["type"], "AeadTest")
        self.assertEqual(ed["testGroups"][0]["type"], "EddsaVerify")
        self.assertEqual(sum(len(g["tests"]) for g in ed["testGroups"]), ed["numberOfTests"])

    def test_library_passes_all_wycheproof_vectors_through_lenient_wrappers(self):
        rows = [r for r in wc.run() if r[0] != "derived_vectors.json"]
        self.assertEqual(wc.failures(rows), [])  # pyca/cryptography itself is fine

    def test_fault_lenient_wrappers_accept_derived_attacks(self):
        bad = {r[1] for r in wc.failures(wc.run())}
        self.assertEqual(bad, {9001, 9002, 9101, 9102})


class TestTiming(unittest.TestCase):
    def test_naive_equal_is_correct(self):
        self.assertTrue(td.naive_equal(b"abc", b"abc"))
        self.assertFalse(td.naive_equal(b"abc", b"abd"))

    def test_early_exit_is_measurable(self):
        early, late = td.experiment(td.naive_equal, rounds=5, reps=1000)
        self.assertGreater(late / early, 1.3)  # 31 extra loop iterations in Python; generous margin for CI noise

    def test_compare_digest_runs(self):  # no timing assertion: noise would make it flaky (see README)
        early, late = td.experiment(hmac.compare_digest, rounds=3, reps=500)
        self.assertGreater(early, 0)


class TestNonce(unittest.TestCase):
    def test_tripwire_and_offline_scan(self):
        key = bytes(32)
        g = ng.GuardedAESGCM(key)
        g.seal(b"\x00" * 12, b"a")
        with self.assertRaises(ng.NonceReuseError):
            g.seal(b"\x00" * 12, b"b")
        runs = [[b"x", b"y"], [b"z", b"w"]]
        self.assertEqual(ng.scan_for_reuse(ng.two_restarts(ng.buggy_nonces, key, runs)).__len__(), 2)
        self.assertEqual(ng.scan_for_reuse(ng.two_restarts(ng.good_nonces, key, runs)), {})


if __name__ == "__main__":
    unittest.main()
