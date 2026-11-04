import unittest

import decision_planning as d


class DecisionPlanningTest(unittest.TestCase):
    def test_expected_attempts_formula(self):
        self.assertAlmostEqual(d.expected_attempts(0.7, 3), 1 + 0.3 + 0.09)
        self.assertEqual(d.expected_attempts(0.0, 8), 8)

    def test_correlated_failures_give_finite_budget(self):
        decay = [0.7 * 0.5**i for i in range(20)]
        self.assertEqual(d.best_budget(decay, 1.0, 20.0), 4)
        self.assertEqual(d.best_budget([0.7] * 20, 1.0, 20.0), 20)

    def test_value_iteration_matches_closed_form(self):
        V, policy, _ = d.value_iteration(d.MDP)
        self.assertAlmostEqual(V["open"], 4 / 0.81, places=6)
        self.assertEqual(policy["open"], "auto")
        self.assertEqual(d.value_iteration(d.make_mdp(0.07))[1]["open"], "escalate")

    def test_astar_optimal_with_admissible_heuristic(self):
        self.assertEqual(d.grid_astar(d.GRID)[0], d.bfs(d.GRID)[0])
        cost, _, _ = d.astar("start", "draft_reply", lambda n: d.PLAN[n], d.H_ADMISSIBLE.get)
        bad, _, _ = d.astar("start", "draft_reply", lambda n: d.PLAN[n], d.H_OVERESTIMATE.get)
        self.assertEqual((cost, bad), (4, 8))

    def test_budgeted_check_can_only_say_unknown(self):
        self.assertTrue(d.dynamic_check(d.collatz_then_delete(27), 100).startswith("unknown"))
        self.assertEqual(d.dynamic_check(d.collatz_then_delete(27), 1000), "calls delete")
        self.assertTrue(d.allow_list_check(d.never_deletes()).startswith("rejected"))


if __name__ == "__main__":
    unittest.main()
