import unittest

import mmc_queue as mq


class TestErlangC(unittest.TestCase):
    def test_textbook_call_centre_example(self):
        # NPTEL (IIT Guwahati) lecture 15: lam=30, mu=12, c=3 -> C(c, r) = 0.702
        self.assertAlmostEqual(mq.erlang_c(3, 30, 12)["P_wait"], 0.702, places=3)

    def test_one_server_reduces_to_mm1(self):
        self.assertAlmostEqual(mq.erlang_c(1, 0.8, 1.0)["Wq"], 4.0)  # M/M/1: lam / (mu (mu - lam))

    def test_unstable_load_is_refused(self):
        with self.assertRaises(ValueError):
            mq.erlang_c(3, 3.0, 1.0)


class TestSimulation(unittest.TestCase):
    def test_reproducible(self):
        self.assertEqual(mq.simulate(5_000, seed=4), mq.simulate(5_000, seed=4))

    def test_matches_erlang_c(self):
        sim, exact = mq.simulate(200_000), mq.erlang_c()
        for key, tol in (("Wq", 0.06), ("Lq", 0.06), ("util", 0.01), ("P_wait", 0.02)):
            with self.subTest(key=key):
                self.assertAlmostEqual(sim[key], exact[key], delta=tol * max(1.0, exact[key]))

    def test_no_wait_when_desks_outnumber_patients(self):
        r = mq.simulate(3, c=3)  # 3 patients, 3 desks: nobody ever waits
        self.assertEqual((r["Wq"], r["P_wait"]), (0.0, 0.0))

    def test_pooling_beats_separate_lines(self):
        self.assertLess(mq.simulate(100_000)["Wq"], mq.simulate(100_000, c=1, lam=mq.LAM / 3)["Wq"] / 2)


try:
    import simpy_mmc
except ImportError:  # SimPy runs in CI only
    simpy_mmc = None


@unittest.skipIf(simpy_mmc is None, "simpy not installed (pending-ci)")
class TestSimPyEquivalent(unittest.TestCase):
    def test_simpy_matches_erlang_c(self):
        sim, exact = simpy_mmc.simulate(200_000), mq.erlang_c()
        self.assertAlmostEqual(sim["Wq"], exact["Wq"], delta=0.06 * exact["Wq"])
        self.assertAlmostEqual(sim["util"], exact["util"], delta=0.01)


if __name__ == "__main__":
    unittest.main()
