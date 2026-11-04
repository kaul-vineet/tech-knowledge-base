"""Tests for lab 17's orchestrator, job queue and backend adapter. Run: python -m unittest -v"""
import unittest

import orchestrator as lab
import solution_cache_key as sol
from backend import Circuit, FakeClock, SimulatorBackend, TransientBackendError


class ExecutionModes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = {m: lab.run(m, key=sol.cache_key) for m in ("sync", "batched", "session")}

    def test_mode_does_not_change_the_answer(self):
        self.assertEqual({o["best_ratio"] for o in self.out.values()}, {0.6922})

    def test_modelled_times(self):
        self.assertEqual([self.out[m]["wall_s"] for m in ("sync", "batched", "session")], [486.8, 66.8, 11.7])
        self.assertEqual([self.out[m]["billed_s"] for m in ("sync", "batched", "session")], [4.8, 4.8, 11.7])

    def test_job_counts(self):
        self.assertEqual([self.out[m]["jobs"] for m in ("sync", "batched", "session")], [240, 30, 30])


class Retries(unittest.TestCase):
    def test_retry_is_idempotent(self):
        clean = lab.run("batched", key=sol.cache_key)
        faulty = lab.run("batched", key=sol.cache_key, fail_jobs=(3, 4, 17))
        self.assertEqual(faulty["retries"], 3)
        self.assertEqual(faulty["best_ratio"], clean["best_ratio"])
        self.assertEqual(faulty["wall_s"] - clean["wall_s"], 10.0)   # 3 extra queue waits + backoff 1 + 2 + 1

    def test_gives_up_after_max_attempts(self):
        clock = FakeClock()
        orch = lab.Orchestrator(SimulatorBackend(clock, fail_jobs=(1, 2, 3, 4)), clock, key=sol.cache_key)
        with self.assertRaises(TransientBackendError):
            orch.submit([Circuit(lab.TEMPLATE, (0.1, 0.2), seed=1)], 16)

    def test_batch_size_limit_is_enforced(self):
        clock = FakeClock()
        backend = SimulatorBackend(clock, max_circuits=5)
        orch = lab.Orchestrator(backend, clock, key=sol.cache_key)
        with self.assertRaises(ValueError):
            orch.submit([Circuit(lab.TEMPLATE, (0.1, 0.2), seed=i) for i in range(6)], 16)


if __name__ == "__main__":
    unittest.main()
