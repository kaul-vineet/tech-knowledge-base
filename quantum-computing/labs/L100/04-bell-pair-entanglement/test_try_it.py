"""Tests for lab 04 try-it items. Run: python -m unittest -v"""
import os
import unittest

import try_it

if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not try_it.HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class TryItNumpy(unittest.TestCase):
    def test_swapped_cx_is_not_entangled(self):
        self.assertEqual(try_it.swapped_cx_numpy(), ({"00": 0.5, "01": 0.5}, 0.0))

    def test_x_after_cx_is_anticorrelated(self):
        self.assertEqual(try_it.x_after_cx_numpy(), ({"01": 0.5, "10": 0.5}, 0.5))


@unittest.skipUnless(try_it.HAVE_QISKIT, "qiskit not installed (runs in CI)")
class TryItSdk(unittest.TestCase):
    def test_qiskit_matches_numpy(self):
        self.assertEqual(try_it.sdk_probabilities("swapped_cx"), try_it.swapped_cx_numpy()[0])
        self.assertEqual(try_it.sdk_probabilities("x_after_cx"), try_it.x_after_cx_numpy()[0])


if __name__ == "__main__":
    unittest.main()
