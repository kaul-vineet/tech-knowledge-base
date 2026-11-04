import math
import random
import unittest

from cryptography.hazmat.primitives.asymmetric import rsa

from nt_toys import (crt, dh_keypair, dh_shared, egcd, is_probable_prime, modinv, rsa_decrypt,
                     rsa_decrypt_crt, rsa_encrypt, rsa_keygen)


class NumberTheory(unittest.TestCase):
    def test_egcd_bezout(self):
        r = random.Random(1)
        for _ in range(500):
            a, b = r.getrandbits(128) + 1, r.getrandbits(128) + 1
            g, x, y = egcd(a, b)
            self.assertEqual(a * x + b * y, g)
            self.assertEqual(g, math.gcd(a, b))

    def test_modinv(self):
        self.assertEqual(modinv(17, 3120), 2753)
        with self.assertRaises(ValueError):
            modinv(6, 9)

    def test_crt(self):
        self.assertEqual(crt([2, 3, 2], [3, 5, 7]), 23)
        for x in range(105):
            self.assertEqual(crt([x % 3, x % 5, x % 7], [3, 5, 7]), x)

    def test_miller_rabin(self):
        primes = {p for p in range(2, 3000) if all(p % d for d in range(2, math.isqrt(p) + 1))}
        for n in range(3000):
            self.assertEqual(is_probable_prime(n), n in primes, n)
        self.assertFalse(is_probable_prime(561))  # Carmichael number

    def test_textbook_rsa_round_trip_and_crt(self):
        key = rsa_keygen(512)
        for m in (0, 1, 42, key["n"] - 1, key["p"]):
            c = rsa_encrypt(m, key)
            self.assertEqual(rsa_decrypt(c, key), m)
            self.assertEqual(rsa_decrypt_crt(c, key), m)

    def test_rsa_with_pyca_key_numbers(self):
        k = rsa.generate_private_key(public_exponent=65537, key_size=2048).private_numbers()
        key = {"n": k.public_numbers.n, "e": 65537, "d": k.d, "p": k.p, "q": k.q}
        m = 123456789
        self.assertEqual(rsa_decrypt_crt(rsa_encrypt(m, key), key), m)
        self.assertEqual(k.iqmp, modinv(k.q, k.p))

    def test_textbook_rsa_is_malleable_and_deterministic(self):
        key = rsa_keygen(512)
        m = 1000
        c = rsa_encrypt(m, key)
        self.assertEqual(rsa_encrypt(m, key), c)
        self.assertEqual(rsa_decrypt(c * pow(3, key["e"], key["n"]) % key["n"], key), 3 * m)

    def test_dh_agreement(self):
        p, g = 23, 5
        a, big_a = dh_keypair(p, g)
        b, big_b = dh_keypair(p, g)
        self.assertEqual(dh_shared(big_b, a, p), dh_shared(big_a, b, p))
        self.assertEqual((pow(5, 6, 23), pow(5, 15, 23), pow(19, 6, 23)), (8, 19, 2))


if __name__ == "__main__":
    unittest.main()
