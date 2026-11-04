import random
import unittest
from fractions import Fraction

from games import (bsgs, composed_scheme, ctr_scheme, ecb_scheme, etm_reduction, gcm_scheme, lwe_instance,
                   posterior_table, regev_bits, run_ind_cca_bitflip, run_ind_cpa, safe_prime, solve_mod,
                   textbook_rsa_forgeries)


class Definitions(unittest.TestCase):
    def test_otp_perfect_secrecy(self):
        prior = {m: Fraction(m + 1, 36) for m in range(8)}
        self.assertTrue(all(v == prior[m] for (m, _), v in posterior_table(3, 3, prior).items()))
        self.assertTrue(any(v != prior[m] for (m, _), v in posterior_table(3, 2, prior).items()))

    def test_ind_cpa(self):
        r = random.Random(1)
        self.assertEqual(run_ind_cpa(ecb_scheme, 50, r), 1.0)
        self.assertEqual(run_ind_cpa(lambda: gcm_scheme(True), 50, r), 1.0)
        self.assertEqual(run_ind_cpa(lambda: composed_scheme("E&M"), 50, r), 1.0)
        self.assertEqual(run_ind_cpa(gcm_scheme, 50, r), 0.0)

    def test_ind_cca(self):
        r = random.Random(2)
        self.assertEqual(run_ind_cca_bitflip(ctr_scheme, 0, 50, r), 1.0)
        self.assertLess(run_ind_cca_bitflip(gcm_scheme, 16, 200, r), 0.25)
        self.assertLess(run_ind_cca_bitflip(lambda: composed_scheme("EtM"), 32, 200, r), 0.25)

    def test_reduction_is_exact_simulation(self):
        a, b = etm_reduction(512, seed=9)
        self.assertEqual(a, b)

    def test_textbook_rsa_not_euf_cma(self):
        a, b = textbook_rsa_forgeries(3233, 17, 2753, random.Random(3), 20)
        self.assertEqual(a, 20)
        self.assertGreaterEqual(b, 18)

    def test_bsgs(self):
        r = random.Random(4)
        p, q = safe_prime(20, r)
        x = r.randrange(1, q)
        self.assertEqual(bsgs(4, pow(4, x, p), p, q)[0], x)

    def test_lwe(self):
        r = random.Random(5)
        s, a, b = lwe_instance(8, 8, 0, r)
        self.assertEqual(solve_mod(a, b), s)
        self.assertEqual(regev_bits(8, 16, 1, 200, r), 0)


if __name__ == "__main__":
    unittest.main()
