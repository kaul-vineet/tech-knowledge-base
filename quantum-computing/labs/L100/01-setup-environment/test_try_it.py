"""Tests for lab 01 try-it items. Run: python -m unittest -v"""
import os
import unittest

import try_it

if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not try_it.HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class TryItNumpy(unittest.TestCase):
    def test_x_twice_returns_to_zero(self):
        self.assertEqual(try_it.x_twice_numpy(), {"0": 100})

    def test_statevector_memory_doubles_per_qubit(self):
        self.assertEqual(try_it.statevector_bytes(3), 128)
        self.assertEqual(try_it.statevector_bytes(30), 16 * 2**30)


@unittest.skipUnless(try_it.HAVE_QISKIT, "qiskit not installed (runs in CI)")
class TryItSdk(unittest.TestCase):
    def test_x_twice_on_sampler(self):
        self.assertEqual(try_it.x_twice_sdk(), try_it.x_twice_numpy())


if __name__ == "__main__":
    unittest.main()
