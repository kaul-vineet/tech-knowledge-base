"""Fitness function: data that must stay secret for years is only exchanged with a PQ-safe group, with no classical
fallback, inside the byte budget. Thresholds: 0 classical-only groups; key shares <= max_handshake_key_share_bytes."""
import contextlib
import io
import json
import unittest
from pathlib import Path

import pq_hybrid as pq
import solution_strict

POLICY = json.loads((Path(__file__).resolve().parent / "pq_policy.json").read_text(encoding="utf-8"))
PQ_SAFE = {pq.GROUP, "ML-KEM-768", "ML-KEM-1024"}  # hybrid or pure ML-KEM; X25519 alone is not


class TestPQPolicyFitness(unittest.TestCase):
    def test_group_is_pq_safe_and_no_fallback(self):
        self.assertIn(POLICY["group"], PQ_SAFE)
        self.assertFalse(POLICY["allow_classical_fallback"])

    def test_handshake_fits_the_budget(self):
        s = pq.sizes()[POLICY["group"]]
        self.assertLessEqual(s["client_share"] + s["server_share"], POLICY["max_handshake_key_share_bytes"])

    def test_deployed_client_refuses_downgrade(self):
        st, ch = pq.client_hello()
        sh, _ = pq.server_respond(ch)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(pq.HandshakeError):
            solution_strict.client_finish(st, sh[-pq.X_LEN:])


if __name__ == "__main__":
    unittest.main()
