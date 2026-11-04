import unittest

import des_queue as dq


class TestDesQueue(unittest.TestCase):
    def test_reproducible_with_seed(self):
        self.assertEqual(dq.simulate(2000, 3), dq.simulate(2000, 3))

    def test_every_customer_served_and_no_negative_wait(self):
        waits, _ = dq.simulate(5000, 3)
        self.assertEqual(len(waits), 5000)
        self.assertGreaterEqual(min(waits), 0.0)

    def test_formula(self):
        self.assertAlmostEqual(dq.mm1_wq(0.8, 1.0), 4.0)
        self.assertAlmostEqual(dq.mm1_wq(0.5, 1.0), 1.0)

    def test_simulation_close_to_mm1(self):
        waits, _ = dq.simulate(200_000, 1)
        self.assertAlmostEqual(sum(waits) / len(waits), dq.mm1_wq(), delta=0.1 * dq.mm1_wq())

    def test_low_load_means_short_waits(self):
        waits, _ = dq.simulate(50_000, 1, lam=0.2)
        self.assertLess(sum(waits) / len(waits), 0.5)


try:
    import simpy_queue
except ImportError:  # SimPy runs in CI only
    simpy_queue = None


@unittest.skipIf(simpy_queue is None, "simpy not installed (pending-ci)")
class TestSimPyEquivalent(unittest.TestCase):
    def test_simpy_matches_formula(self):
        waits = simpy_queue.simulate(200_000, 1)
        self.assertAlmostEqual(sum(waits) / len(waits), dq.mm1_wq(), delta=0.1 * dq.mm1_wq())


if __name__ == "__main__":
    unittest.main()
