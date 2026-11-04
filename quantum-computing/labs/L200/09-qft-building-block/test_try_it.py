"""Tests for lab 09 try-it items. Run: python -m unittest -v"""
import os
import unittest

import try_it

if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not try_it.HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class TryItNumpy(unittest.TestCase):
    def test_no_swaps_is_dft_with_bit_reversed_rows(self):
        self.assertEqual(try_it.no_swaps_numpy(), {"max_error_vs_dft": 0.7071, "after_bit_reversing_rows": 0.0})

    def test_negated_angles_give_the_inverse_transform(self):
        self.assertEqual(try_it.negated_angles_numpy(), {"max_error_vs_dft": 0.7071, "max_error_vs_np_fft_fft": 0.0})


@unittest.skipUnless(try_it.HAVE_QISKIT, "qiskit not installed (runs in CI)")
class TryItSdk(unittest.TestCase):
    def test_qiskit_matches_numpy(self):
        self.assertEqual(try_it.sdk_versions(), {"no_swaps_equals_dft": False, "no_swaps_bit_reversed_equals_dft": True,
                                                 "negated_equals_np_fft_fft": True})


if __name__ == "__main__":
    unittest.main()
