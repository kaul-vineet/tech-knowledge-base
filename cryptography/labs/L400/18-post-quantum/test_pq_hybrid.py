"""Lab tests: sizes from FIPS 203 / RFC 10024, hybrid handshake, and why hybrid survives one broken component."""
import unittest

import pq_hybrid as pq


class TestPQHybrid(unittest.TestCase):
    def test_sizes_match_the_standards(self):
        s = pq.sizes()
        self.assertEqual((s["ML-KEM-768"]["client_share"], s["ML-KEM-768"]["server_share"]), (1184, 1088))
        self.assertEqual((s["ML-KEM-1024"]["client_share"], s["ML-KEM-1024"]["server_share"]), (1568, 1568))
        self.assertEqual((s[pq.GROUP]["client_share"], s[pq.GROUP]["server_share"], s[pq.GROUP]["secret"]), (1216, 1120, 64))

    def test_hybrid_handshake_agrees(self):
        st, ch = pq.client_hello()
        sh, ks = pq.server_respond(ch)
        self.assertEqual(pq.client_finish(st, sh), (ks, pq.GROUP))

    def test_broken_x25519_alone_does_not_reveal_hybrid_key(self):
        st, ch = pq.client_hello()
        sh, ks = pq.server_respond(ch)
        self.assertNotEqual(pq.harvest_then_break(st, sh), ks)

    def test_broken_mlkem_alone_does_not_reveal_hybrid_key(self):
        st, ch = pq.client_hello()
        sh, ks = pq.server_respond(ch)
        ss_pq = st["mlkem"].decapsulate(sh[:pq.MLKEM_CT])  # attacker somehow has the ML-KEM secret ...
        guess = pq.derive(ss_pq + bytes(32), ch, sh)  # ... but not the X25519 one
        self.assertNotEqual(guess, ks)

    def test_key_bound_to_transcript(self):
        st, ch = pq.client_hello()
        sh, ks = pq.server_respond(ch)
        secret = st["mlkem"].decapsulate(sh[:pq.MLKEM_CT]) + st["x"].exchange(pq.x25519.X25519PublicKey.from_public_bytes(sh[pq.MLKEM_CT:]))
        self.assertEqual(pq.derive(secret, ch, sh), ks)
        self.assertNotEqual(pq.derive(secret, ch, sh[:-1] + b"\x00"), ks)

    def test_server_rejects_bad_client_share(self):
        with self.assertRaises(pq.HandshakeError):
            pq.server_respond(b"\x00" * 32)


if __name__ == "__main__":
    unittest.main()
