"""Build-task check for lab 11. Run: python -m unittest test_build_task -v

Checks solution_chain.py by default; to check your own file set BUILD_TASK_MODULE, e.g.
  macOS:   BUILD_TASK_MODULE=my_chain python -m unittest test_build_task -v
  Windows: $env:BUILD_TASK_MODULE = "my_chain"; python -m unittest test_build_task -v
"""
import importlib
import importlib.util
import os
import unittest

mod = importlib.import_module(os.environ.get("BUILD_TASK_MODULE", "solution_chain"))
HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None


class ChainNumpy(unittest.TestCase):
    def test_same_state_and_line_friendly(self):
        self.assertEqual(mod.chain_numpy(), {"same_state_as_star": True, "non_adjacent_on_line": []})


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class ChainSdk(unittest.TestCase):
    def test_chain_needs_no_swaps_on_line(self):
        out = mod.compare_on_line()
        self.assertEqual(out["chain"], [4, 4, 4, 4])
        self.assertTrue(all(c <= s for c, s in zip(out["chain"], out["star"])))
        self.assertGreater(out["star"][0], 4)


if __name__ == "__main__":
    unittest.main()
