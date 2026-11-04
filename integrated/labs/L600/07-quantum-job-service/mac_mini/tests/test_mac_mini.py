"""Tests for project 07's Mac mini scripts at sandbox size (python -m unittest discover -s mac_mini/tests).
The Aer tests run only where qiskit + qiskit-aer are installed (pendingMac here); everything else runs anywhere."""
import contextlib
import io
import json
import sys
import unittest
from pathlib import Path

MAC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MAC))
import aer_backend as ab  # noqa: E402
import backends as bk  # noqa: E402
import overnight_load  # noqa: E402
import qubit_sweep  # noqa: E402


def lines(fn, argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = fn(argv)
    return code, [json.loads(x) for x in buf.getvalue().splitlines() if x.startswith("{")]


class Conformance(unittest.TestCase):
    def test_numpy_backend_passes_the_interface_contract(self):
        res = ab.conformance(ab.like(bk.fleet(7)[0], bk.Backend))
        self.assertTrue(all(res.values()), res)

    def test_contract_catches_a_backend_that_resamples_on_retry(self):
        class Unseeded(bk.Backend):
            calls = 0

            def execute(self, n, ops, version, shots, seed, chunk):
                Unseeded.calls += 1  # a re-executed attempt gets new samples: breaks the lease/fencing contract
                return super().execute(n, ops, version, shots, seed + Unseeded.calls, chunk)
        res = ab.conformance(ab.like(bk.fleet(7)[0], Unseeded))
        self.assertFalse(res["same_attempt_same_counts"])

    @unittest.skipIf(ab.have_aer(), "Aer installed: the real adapter is tested instead")
    def test_missing_aer_is_a_skip_here_and_an_error_on_the_mac(self):
        code, rows = lines(ab.main, ["--here"])
        self.assertEqual((code, rows[-1]["aer"]), (0, "skipped"))
        self.assertEqual(lines(ab.main, [])[0], 2)

    @unittest.skipUnless(ab.have_aer(), "needs qiskit + qiskit-aer (pendingMac)")
    def test_aer_backend_conforms_and_agrees_with_numpy(self):
        for b in bk.fleet(7):
            res = ab.conformance(ab.like(b, ab.AerBackend), reference=ab.like(b, bk.Backend))
            self.assertTrue(res["agrees_with_numpy_backend"], res)
            self.assertTrue(res["same_attempt_same_counts"], res)


class Sweep(unittest.TestCase):
    def test_walls_follow_the_memory_maths(self):
        w = qubit_sweep.walls(10.0)   # 16 x 2^29 = 8.6 GB <= 10 GB < 16 x 2^30; 16 x 4^14 = 4.3 GB <= 10 < 16 x 4^15
        self.assertEqual((w["statevector_c128"], w["density_matrix_c128"]), (29, 14))

    def test_ghz_numpy_runs_give_two_peaks(self):
        state = qubit_sweep.numpy_sv(6)()
        p = abs(state) ** 2
        self.assertAlmostEqual(p[0] + p[-1], 1.0)


class Overnight(unittest.TestCase):
    def test_one_run_with_a_doubled_fleet_keeps_the_contract(self):
        row = overnight_load.one((2, 7, 120))
        self.assertEqual(row["backends"], 6)
        self.assertEqual(row["shots_exact"], row["jobs"])
        self.assertEqual(row["contract_violations"], 0)
        self.assertEqual(bk.fleet.__qualname__, "fleet")  # the module's own fleet() is restored afterwards


if __name__ == "__main__":
    unittest.main()
