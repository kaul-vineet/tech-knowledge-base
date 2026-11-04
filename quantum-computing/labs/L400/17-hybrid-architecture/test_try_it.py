"""Tests for lab 17 try-it items and the Qiskit path (CI). Run: python -m unittest -v"""
import importlib.util
import os
import unittest

import try_it

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class TryIt(unittest.TestCase):
    def test_busy_queue_widens_the_gap(self):
        self.assertEqual(try_it.busy_queue(), {"sync": (7206.8, 4.8), "batched": (906.8, 4.8), "session": (39.7, 39.7)})

    def test_session_ttl_expiry_loses_the_advantage_and_bills_the_window(self):
        out = try_it.slow_classical_step()
        self.assertEqual(out["session"][0], out["batched"][0])
        self.assertEqual(out["session"], (2165.3, 2165.3))


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class QiskitPath(unittest.TestCase):
    def test_batched_uses_one_job_per_step_and_one_transpile(self):
        import sampler_qiskit as sq
        sq.COUNTERS.update(transpiles=0, jobs=0)
        out = sq.run("batched", iters=5)
        self.assertEqual((out["transpiles"], out["jobs"]), (1, 5))
        sq.COUNTERS.update(transpiles=0, jobs=0)
        self.assertEqual(sq.run("sync", iters=5)["jobs"], 40)


if __name__ == "__main__":
    unittest.main()
