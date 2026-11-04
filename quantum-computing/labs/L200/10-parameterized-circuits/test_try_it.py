"""Tests for lab 10 try-it items. Run: python -m unittest -v"""
import os
import unittest

import try_it

if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not try_it.HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class TryItNumpy(unittest.TestCase):
    def test_rx_keeps_z_and_kills_x(self):
        self.assertEqual(try_it.rx_instead_of_ry_numpy(), {"fit_Z": [1.0, 0.0, 0.0], "fit_X": [0.0, 0.0, 0.0]})

    def test_fewer_shots_worse_fit(self):
        out = try_it.fewer_shots_numpy()
        self.assertGreater(out[25]["worst_error"], out[400]["worst_error"])
        self.assertLess(out[400]["worst_error"], 0.05)


@unittest.skipUnless(try_it.HAVE_QISKIT, "qiskit not installed (runs in CI)")
class TryItSdk(unittest.TestCase):
    def test_qiskit_matches_numpy(self):
        out = try_it.sdk_results()
        self.assertEqual((out["fit_Z"], out["fit_X"]), ([1.0, 0.0, 0.0], [0.0, 0.0, 0.0]))
        self.assertLess(out["worst_error_by_shots"][400], 0.05)


if __name__ == "__main__":
    unittest.main()
