import unittest

import numpy as np

import inventory as inv


class TestInventory(unittest.TestCase):
    def test_streams_are_reproducible_and_purpose_separated(self):
        d1, l1 = inv.streams(3)
        d2, l2 = inv.streams(3)
        np.testing.assert_array_equal(d1, d2)
        np.testing.assert_array_equal(l1, l2)
        self.assertTrue(set(np.unique(l1)) <= {1, 2, 3, 4})

    def test_hand_case_no_demand_costs_only_holding(self):
        r = inv.simulate(5, 10, np.zeros(4, dtype=int), np.ones(4, dtype=int))
        self.assertEqual((r["orders"], r["lost"]), (0, 0))
        self.assertAlmostEqual(r["cost_per_day"], inv.HOLD * 10)

    def test_hand_case_order_up_to_S_and_lead_time(self):
        # day 0: 10 on hand, demand 7 -> 3 left <= s=5 -> order 7, arrives morning of day 2 (lead 2)
        demand, lead = np.array([7, 2, 0]), np.array([2, 2, 2])
        r = inv.simulate(5, 10, demand, lead)
        self.assertEqual((r["orders"], r["lost"]), (1, 0))
        self.assertAlmostEqual(r["cost_per_day"], (inv.HOLD * (3 + 1 + 8) + inv.ORDER) / 3)

    def test_lost_sales_are_counted(self):
        r = inv.simulate(0, 5, np.array([8]), np.array([1]))
        self.assertEqual(r["lost"], 3)

    def test_crn_narrows_the_comparison(self):
        _, h_ind = inv.compare((30, 80), (30, 90), crn=False)
        m, h_crn = inv.compare((30, 80), (30, 90), crn=True)
        self.assertLess(h_crn * 2, h_ind)
        self.assertLess(m + h_crn, 0)  # with CRN the cheaper policy is identified


try:
    import simpy_inventory
except ImportError:  # SimPy runs in CI only
    simpy_inventory = None


@unittest.skipIf(simpy_inventory is None, "simpy not installed (pending-ci)")
class TestSimPyEquivalent(unittest.TestCase):
    def test_container_model_gives_identical_results(self):
        for rep in range(3):
            d, lead = inv.streams(rep)
            for pol in ((20, 80), (30, 90)):
                a, b = inv.simulate(*pol, d, lead), simpy_inventory.simulate(*pol, d, lead)
                self.assertEqual((a["orders"], a["lost"]), (b["orders"], b["lost"]))
                self.assertAlmostEqual(a["cost_per_day"], b["cost_per_day"], places=9)


if __name__ == "__main__":
    unittest.main()
