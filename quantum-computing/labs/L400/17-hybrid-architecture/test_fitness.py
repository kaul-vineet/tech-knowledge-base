"""Fitness function for lab 17: keeps ADR 0001 (batched jobs + structural transpile cache) true.
Run: python -m unittest test_fitness -v   (same BUILD_TARGET / BUILD_TASK_MODULE switch as test_build_task)

Thresholds for the reference workload (4 starts x 30 SPSA iterations = 240 circuits):
  jobs <= iterations (one job per optimizer step) · transpiles == 1 · modelled wall <= 90 s · billed <= 5 s.
"""
import unittest

import buildtarget
import orchestrator as lab

mod = buildtarget.load("solution_cache_key", "my_cache_key")


class ExecutionDesignFitness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = lab.run(lab.DEFAULT_MODE, key=mod.cache_key)

    def test_default_mode_is_the_adr_decision(self):
        self.assertEqual(lab.DEFAULT_MODE, "batched")

    def test_one_job_per_optimizer_step(self):
        self.assertLessEqual(self.out["jobs"], lab.WORKLOAD["iters"])

    def test_compile_once(self):
        self.assertEqual(self.out["transpiles"], 1)

    def test_wall_and_billing_budget(self):
        self.assertLessEqual(self.out["wall_s"], 90.0)    # modelled (FakeClock), not real time
        self.assertLessEqual(self.out["billed_s"], 5.0)


if __name__ == "__main__":
    unittest.main()
