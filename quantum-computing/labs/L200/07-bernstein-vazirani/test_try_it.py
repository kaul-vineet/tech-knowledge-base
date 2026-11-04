"""Tests for lab 07 try-it items. Run: python -m unittest -v"""
import os
import unittest

import try_it

if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not try_it.HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class TryItNumpy(unittest.TestCase):
    def test_no_kickback_reads_all_zeros(self):
        self.assertEqual(try_it.no_kickback_numpy(), {"0000": 1.0})

    def test_unreversed_oracle_reads_reversed_secret(self):
        self.assertEqual(try_it.unreversed_oracle_numpy(), {"1101": 1.0})


@unittest.skipUnless(try_it.HAVE_QISKIT, "qiskit not installed (runs in CI)")
class TryItSdk(unittest.TestCase):
    def test_qiskit_matches_numpy(self):
        self.assertEqual(try_it.sdk_counts("no_kickback"), {"0000": 100})
        self.assertEqual(try_it.sdk_counts("unreversed"), {"1101": 100})


if __name__ == "__main__":
    unittest.main()
