"""python -m unittest -v   (smaller runs than the demo; same invariants)"""
import random
import unittest

import perf_proofs as pp


class PerfTests(unittest.TestCase):
    def test_mm1_mean_sojourn(self):
        rng = random.Random(3)
        arr, dep = pp.simulate_queue(rng, 100_000, lambda r: r.expovariate(0.8), lambda r: r.expovariate(1.0))
        w = sum(d - a for a, d in zip(arr, dep)) / len(arr)
        self.assertAlmostEqual(w, 5.0, delta=0.5)

    def test_little_exact_on_empty_window(self):
        out = "\n".join(pp.check_little(n=20_000))
        diff = float(out.split("relative difference ")[1].split()[0])
        self.assertLess(diff, 1e-9)

    def test_tail_formula(self):
        out = "\n".join(pp.check_tail(requests=5_000))
        self.assertIn("1 - 0.99^n = 0.6340", out)

    def test_usl_peak(self):
        import math
        best = max(range(1, 500), key=lambda p: pp.usl(p, 0.1, 0.001))
        self.assertEqual(best, round(math.sqrt(0.9 / 0.001)))
        self.assertLess(pp.amdahl(10_000, 0.05), 20)


if __name__ == "__main__":
    unittest.main()
