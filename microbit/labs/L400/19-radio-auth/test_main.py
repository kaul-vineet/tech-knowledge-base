"""Lab 19 basics: SipHash-2-4 reference vectors, the toy tag's weakness, counter reservation, CRC verifier."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import frame_auth as fa  # noqa: E402
import cost  # noqa: E402
from verifier import Verifier  # noqa: E402

# veorq/SipHash vectors.h, vectors_sip64[i]: key 00..0f, message 00..(i-1), output little-endian
VECTORS = {0: "310e0edd47db6f72", 1: "fd67dc93c539f874", 2: "5a4fa9d909806c0d",
           15: "e545be4961ca29a1", 63: "724506eb4c328a95"}


class Mac(unittest.TestCase):
    def test_siphash_reference_vectors(self):
        key = bytes(range(16))
        for n, expect in VECTORS.items():
            self.assertEqual(fa.siphash24(key, bytes(range(n))).to_bytes(8, "little").hex(), expect, n)

    def test_toy_tag_is_a_crc_with_a_16_bit_secret_state(self):
        key, msg = b"0123456789abcdef", b"n1:7:21,100,0"
        self.assertEqual(fa.toy_tag(key, msg), fa.crc16(msg, fa.crc16(key)))   # key collapses to 16 bits

    def test_crc_frame_passes_the_before_verifier(self):
        v = Verifier()
        self.assertEqual(v.check(fa.seal("n1", 7, "21,100,0", None, "crc")), ("n1", 7, "21,100,0"))
        self.assertIsNone(v.check("n1:7:21,100,0:0000"))
        self.assertIn('"reject": "crc"', v.log[-1])


class CounterReservation(unittest.TestCase):
    def test_reset_skips_ahead_and_flash_writes_are_rare(self):
        flash = {"v": 0}
        c = fa.Counter(lambda: flash["v"], lambda v: flash.update(v=v), block=100)
        used = [c.take() for _ in range(150)]
        self.assertEqual((used[-1], flash["v"], c.writes), (150, 200, 2))
        after_reset = fa.Counter(lambda: flash["v"], lambda v: flash.update(v=v), block=100)
        self.assertEqual(after_reset.take(), 201)              # never reuses 151..200
        self.assertEqual(cost.flash_writes(), 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
