"""Verification suite for the clinic queue model (L200 lesson 8): is the CODE right? (Sargent 2010 techniques)

Run alone with `python -m unittest verification -v`; governance.py runs it and stores the counts as evidence.
"""
import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "L200" / "08-multi-server-queue"))
import mmc_queue as mq  # noqa: E402


class DegenerateTests(unittest.TestCase):
    def test_one_desk_reduces_to_mm1(self):
        self.assertAlmostEqual(mq.erlang_c(1, 0.8, 1.0)["Wq"], 4.0)  # analytic M/M/1: lam / (mu (mu - lam))

    def test_no_wait_when_desks_outnumber_patients(self):
        self.assertEqual(mq.simulate(3, c=3)["Wq"], 0.0)


class ExtremeConditionTests(unittest.TestCase):
    def test_overload_is_refused_not_simulated_quietly(self):
        with self.assertRaises(ValueError):
            mq.erlang_c(3, 3.0, 1.0)

    def test_light_load_almost_never_waits(self):
        self.assertLess(mq.simulate(20_000, c=3, lam=0.3, seed=2)["P_wait"], 0.01)


class InternalValidityTests(unittest.TestCase):
    def test_same_seed_same_result(self):
        self.assertEqual(mq.simulate(5_000, seed=4), mq.simulate(5_000, seed=4))

    def test_littles_law_inside_the_simulation(self):
        r = mq.simulate(50_000, seed=5)
        self.assertAlmostEqual(r["Lq"], mq.LAM * r["Wq"], delta=0.05 * r["Lq"])

    def test_pooling_beats_separate_lines(self):
        self.assertLess(mq.simulate(50_000)["Wq"], mq.simulate(50_000, c=1, lam=mq.LAM / 3)["Wq"] / 2)


if __name__ == "__main__":
    unittest.main()
