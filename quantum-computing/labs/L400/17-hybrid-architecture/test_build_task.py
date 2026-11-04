"""Build-task check for lab 17 (transpile-cache key). Run: python -m unittest test_build_task -v

Checks solution_cache_key.py by default. Your file: write my_cache_key.py with cache_key(template, params, backend, opt_level=1)
  macOS:   BUILD_TARGET=mine python -m unittest test_build_task -v
  Windows: $env:BUILD_TARGET = "mine"; python -m unittest test_build_task -v
failureLab proof: BUILD_TASK_MODULE=orchestrator (naive key with parameter values) FAILS test_one_transpile_per_structure.
"""
import unittest

import buildtarget
import orchestrator as lab
from backend import FakeClock, SimulatorBackend, Template

mod = buildtarget.load("solution_cache_key", "my_cache_key")


class CacheKey(unittest.TestCase):
    def setUp(self):
        self.backend = SimulatorBackend(FakeClock())

    def test_one_transpile_per_structure(self):
        out = lab.run("batched", key=mod.cache_key)
        self.assertEqual(out["transpiles"], 1)
        self.assertEqual(out["cache_hits"], out["circuits"] - 1)

    def test_same_structure_new_angles_same_key(self):
        k = lambda params: mod.cache_key(lab.TEMPLATE, params, self.backend)  # noqa: E731
        self.assertEqual(k((0.1, 0.2)), k((0.7, 1.1)))

    def test_no_stale_reuse_across_targets_depth_or_level(self):
        other = SimulatorBackend(FakeClock(), target="heavy-hex-27")
        deeper = Template("qaoa-maxcut", 8, lab.TEMPLATE.edges, 2)
        base = mod.cache_key(lab.TEMPLATE, (0.1, 0.2), self.backend)
        self.assertNotEqual(base, mod.cache_key(lab.TEMPLATE, (0.1, 0.2), other))
        self.assertNotEqual(base, mod.cache_key(deeper, (0.1, 0.2, 0.3, 0.4), self.backend))
        self.assertNotEqual(base, mod.cache_key(lab.TEMPLATE, (0.1, 0.2), self.backend, opt_level=3))


if __name__ == "__main__":
    unittest.main()
