"""Fitness functions F1-F3 on seeds the design was not tuned on (5 and 6), plus the gossip experiment."""
import unittest

from tests._shared import run
import _kb  # noqa: E402
import fleet_sim  # noqa: E402
import run_project  # noqa: E402


class F1ZeroLoss(unittest.TestCase):
    def test_other_seeds(self):
        for seed in (5, 6):
            r = run(seed=seed)
            self.assertEqual((r["lost"], r["wrong_values"], r["replicas_equal"]), (0, 0, True), seed)


class F2Convergence(unittest.TestCase):
    def test_push_pull_rounds(self):
        exp = fleet_sim.convergence_experiment(trials=100, seed=7)
        self.assertLessEqual(exp["max"], run_project.MAX_ROUNDS)
        self.assertLessEqual(run(seed=5)["convergence_rounds"], run_project.MAX_ROUNDS)


class F3Battery(unittest.TestCase):
    def test_every_device_meets_the_target(self):
        for seed in (4, 5):
            self.assertGreaterEqual(run(seed=seed)["life_h_min"], run_project.TARGET_LIFE_H)

    def test_target_fails_with_a_10_s_sync_and_3_tries(self):
        fig = dict(_kb.budget().FIGURES)
        # 60 samples x 20 ms + 360 syncs/h x (20 + 3 x 50) ms: radio retries on every 10 s sync
        self.assertLess(fleet_sim.life_hours(1200 + 360 * 170, 3600 * 1000, fig)[0], run_project.TARGET_LIFE_H)


if __name__ == "__main__":
    unittest.main()
