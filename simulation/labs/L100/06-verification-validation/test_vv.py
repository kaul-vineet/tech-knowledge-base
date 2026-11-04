import unittest

import vv


class TestVerification(unittest.TestCase):
    """Verification: is the code doing what the model says?"""

    def test_rule_hand_cases(self):
        self.assertEqual(vv.next_wait(0.0, 3.0, 1.0), 2.0)  # next customer arrives while 2 min of work remain
        self.assertEqual(vv.next_wait(2.0, 1.0, 5.0), 0.0)  # server idle before next arrival -> no wait

    def test_first_customer_never_waits(self):
        self.assertEqual(vv.waits(10, 0.8, 1)[0], 0.0)

    def test_waits_never_negative(self):
        self.assertGreaterEqual(min(vv.waits(20_000, 0.8, 3)), 0.0)

    def test_reproducible(self):
        self.assertEqual(vv.waits(1000, 0.8, 1), vv.waits(1000, 0.8, 1))
        self.assertNotEqual(vv.waits(1000, 0.8, 1), vv.waits(1000, 0.8, 2))


class TestValidation(unittest.TestCase):
    """Validation: does the model agree with a trusted reference (here the M/M/1 formula)?"""

    def test_ci_contains_formula(self):
        m, half = vv.replicate(0.8)
        self.assertLessEqual(abs(m - vv.formula(0.8)), half)

    def test_sensitivity_is_monotonic(self):
        results = [vv.replicate(lam, reps=10, n=20_000)[0] for lam in (0.5, 0.7, 0.9)]
        self.assertEqual(results, sorted(results))


try:
    from scipy import stats
except ImportError:  # SciPy runs in CI only
    stats = None


@unittest.skipIf(stats is None, "scipy not installed (pending-ci)")
class TestTQuantile(unittest.TestCase):
    def test_t_975_9_matches_scipy(self):
        self.assertAlmostEqual(vv.T_975[9], stats.t.ppf(0.975, 9), places=3)


if __name__ == "__main__":
    unittest.main()
