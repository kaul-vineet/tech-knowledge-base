"""Build task check (failureLab proof). Default: tests solution_verified.py.
Test YOUR version (the shipped threat_model.py trusts any NAMED control):
  macOS    BUILD_TARGET=mine python -m unittest -v test_build_task
  Windows  $env:BUILD_TARGET="mine"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_TARGET
BUILD_IMPL=<module> picks any other module."""
import importlib
import os
import random
import unittest

import threat_model as tm

MODULE = "threat_model" if os.environ.get("BUILD_TARGET") == "mine" else os.environ.get("BUILD_IMPL", "solution_verified")
impl = importlib.import_module(MODULE)


class TestModelDriftIsCaught(unittest.TestCase):
    def test_clean_model_passes(self):
        self.assertEqual(impl.check(tm.load()), [])

    def test_deleted_test_is_reported(self):
        m = tm.load()
        victim = tm.inject_drift(m, random.Random(tm.SEED))
        self.assertTrue(any(p.startswith(f"{victim}: test missing") for p in impl.check(m)))

    def test_unmodelled_boundary_flow_is_reported(self):
        m = tm.load()
        tm.inject_drift(m, random.Random(tm.SEED))
        problems = impl.check(m)
        self.assertIn("app-log->siem: boundary-crossing flow lacks T", problems)
        self.assertIn("app-log->siem: boundary-crossing flow lacks I", problems)

    def test_unverified_control_does_not_close_the_attack_tree(self):
        m = tm.load()
        tm.inject_drift(m, random.Random(tm.SEED))
        cost, _ = tm.cheapest(m["attack_tree"], impl.verified_controls(m))
        self.assertEqual(cost, 8)


if __name__ == "__main__":
    unittest.main()
