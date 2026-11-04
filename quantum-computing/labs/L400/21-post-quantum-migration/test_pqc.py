"""Tests for lab 21: Shor context, plan priorities, agility (ML-KEM-768 runs locally). Run: python -m unittest -v"""
import json
import unittest

import agility
import pqc_lab as lab
import shor_context
import solution_scanner as scanner


class ShorContext(unittest.TestCase):
    def test_our_model_and_ecc_formula(self):
        self.assertEqual(shor_context.our_model(), {"workload": "rsa-2048", "logical_qubits": 6190, "distance": 27,
                                                    "physical_qubits": 9025020, "runtime_s": 57870.0})
        self.assertEqual(shor_context.ecc_logical(256), {"workload": "ecc-p256", "logical_qubits": 2330,
                                                         "toffoli": 128748355584})


class Plan(unittest.TestCase):
    def test_grep_misses_the_hndl_critical_items(self):
        steps = lab.plan(lab.scan())
        self.assertEqual(len(steps), 5)
        self.assertFalse(any(s["priority"].startswith("P1") for s in steps))
        self.assertIn(("toy_app/auth.py", 1), {(s["file"], s["line"]) for s in steps})      # a docstring

    def test_priorities_from_mosca(self):
        p1 = {(s["file"], s["line"]) for s in lab.plan(scanner.scan()) if s["priority"].startswith("P1")}
        self.assertEqual(p1, {("toy_app/billing.py", 7), ("toy_app/sync.py", 7)})


class Agility(unittest.TestCase):
    def test_every_kem_round_trips_through_the_envelope(self):
        for name, kem in agility.REGISTRY.items():
            sk, pk = kem.keygen()
            key, envelope = agility.establish(pk, name)
            self.assertEqual(agility.accept(sk, envelope), key)
            self.assertEqual(json.loads(envelope)["kem"], name)

    def test_sizes(self):
        sizes = {n: (agility.measure(n, rounds=2)["public_key_bytes"], agility.measure(n, rounds=2)["ciphertext_bytes"])
                 for n in agility.REGISTRY}
        self.assertEqual(sizes, {"x25519": (32, 32), "ml-kem-768": (1184, 1088), "x25519+ml-kem-768": (1216, 1120)})

    def test_hybrid_key_depends_on_both_secrets(self):
        h = agility.REGISTRY["x25519+ml-kem-768"]
        self.assertNotEqual(h.combine(b"a" * 32, b"b" * 32), h.combine(b"a" * 32, b"c" * 32))
        self.assertNotEqual(h.combine(b"a" * 32, b"b" * 32), h.combine(b"d" * 32, b"b" * 32))


if __name__ == "__main__":
    unittest.main()
