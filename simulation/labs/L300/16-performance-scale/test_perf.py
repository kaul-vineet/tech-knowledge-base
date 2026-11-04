import unittest

import numpy as np

import perf


class TestVectorisation(unittest.TestCase):
    def test_vectorised_equals_loop(self):
        s, g = perf.draws(np.random.SeedSequence(1), n=5_000)
        self.assertAlmostEqual(perf.mean_wait_vectorised(s, g), perf.mean_wait_loop(s, g), places=10)

    def test_lindley_by_hand(self):
        service, gaps = np.array([2.0, 1.0, 3.0, 1.0]), np.array([0.0, 1.0, 5.0, 1.0])
        # waits: 0, max(0, 0+2-1)=1, max(0, 1+1-5)=0, max(0, 0+3-1)=2 -> mean 0.75
        self.assertAlmostEqual(perf.mean_wait_loop(service, gaps), 0.75)
        self.assertAlmostEqual(perf.mean_wait_vectorised(service, gaps), 0.75)

    def test_vectorised_works_on_a_batch_of_replications(self):
        data = [perf.draws(c, n=1_000) for c in np.random.SeedSequence(2).spawn(3)]
        batch = perf.mean_wait_vectorised(np.array([s for s, _ in data]), np.array([g for _, g in data]))
        np.testing.assert_allclose(batch, [perf.mean_wait_loop(s, g) for s, g in data], rtol=1e-12)


class TestFailureLab(unittest.TestCase):
    """Fault: every task carries the same seed. Your fix to tasks_for() is checked by test_build_task.py."""

    def test_fault_shared_seed_gives_identical_replications(self):
        bad = perf.run_parallel([(rep, perf.SEED) for rep in range(6)], 2)  # what the shipped tasks_for() builds
        self.assertEqual(len(set(bad.tolist())), 1)
        self.assertAlmostEqual(perf.ci(bad)[1], 0.0, places=12)  # a zero-width 'confidence interval' is a red flag, not precision

    def test_spawned_children_are_distinct_and_worker_count_independent(self):
        tasks = list(enumerate(np.random.SeedSequence(perf.SEED).spawn(6)))
        one, two = perf.run_parallel(tasks, 1), perf.run_parallel(tasks, 2)
        self.assertEqual(len(set(two.tolist())), 6)
        np.testing.assert_array_equal(one, two)


if __name__ == "__main__":
    unittest.main()
