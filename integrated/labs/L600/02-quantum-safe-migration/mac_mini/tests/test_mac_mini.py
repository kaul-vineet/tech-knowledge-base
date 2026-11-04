"""Tests for project 02's Mac mini scripts at sandbox size (python -m unittest discover -s mac_mini/tests).
Behaviour only: exact sizes, decisions, skip paths and the wall maths; never timings."""
import contextlib
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path

MAC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MAC))
import _mac  # noqa: E402
import order_wall  # noqa: E402
import pq_bench  # noqa: E402
import qiskit_crosscheck as qc  # noqa: E402

HAVE_QISKIT = all(importlib.util.find_spec(m) for m in ("qiskit", "qiskit_aer"))


def lines(fn, argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = fn(argv)
    return code, [json.loads(x) for x in buf.getvalue().splitlines() if x.startswith("{")]


class PqBench(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code, cls.rows = lines(pq_bench.main, ["--here"])

    def test_exact_sizes_from_the_library(self):
        by = {r["alg"]: r for r in self.rows if "alg" in r}
        self.assertEqual((by["ML-KEM-768"]["ek_B"], by["ML-KEM-768"]["ct_B"]), (1184, 1088))
        self.assertEqual(by["ML-DSA-65"]["sig_B"], 3309)
        self.assertEqual(by["ML-DSA-87"]["sig_B"], 4627)

    def test_ml_kem_512_reported_unavailable_not_invented(self):
        row = next(r for r in self.rows if r.get("alg") == "ML-KEM-512")
        self.assertFalse(row["available"])

    def test_budget_rules_out_ml_kem_1024_by_bytes(self):
        dec = self.rows[-1]
        self.assertEqual(self.code, 0)
        for o in dec["options"]:
            self.assertEqual(o["share_fits_client_flight"], o["kem"] == "ML-KEM-768")
            self.assertEqual(o["client_key_share_B"], 1216 if o["kem"] == "ML-KEM-768" else 1600)


class OrderWall(unittest.TestCase):
    def test_three_qubits_per_bit_of_n(self):
        self.assertEqual([order_wall.qubits(m) for m in (15, 21, 35, 323, 899)], [12, 15, 18, 27, 30])

    def test_pick_a_gives_a_splitting_base(self):
        for m in order_wall.SEMIPRIMES[:5]:
            a = order_wall.pick_a(m)
            r = order_wall.shor_sim.l25.order(a, m)
            self.assertEqual(r % 2, 0)
            self.assertNotEqual(pow(a, r // 2, m), m - 1)

    def test_wall_is_computed_from_bytes_per_amplitude(self):
        w = order_wall.wall(16, 10.0)  # 16 B/amp, 10 GB: N=323 (27 q) needs 2.1 GB, N=899 (30 q) 17.2 GB
        self.assertEqual((w["largest_N"], w["next_N"]), (323, 899))
        self.assertEqual(order_wall.wall(128, 10.0)["largest_N"], 143)

    def test_n15_runs_and_factors(self):
        r = order_wall.run_one(15)
        self.assertEqual(r["factors"], [3, 5])
        self.assertGreater(r["bytes_per_amplitude"], 16)  # the simulator needs more than the textbook state


class QiskitCrossCheck(unittest.TestCase):
    def test_tvd(self):
        self.assertAlmostEqual(qc.tvd([1, 0], [0, 1]), 1.0)
        self.assertAlmostEqual(qc.tvd([2, 2], [1, 1]), 0.0)

    def test_counts_use_little_endian_bit_order(self):
        self.assertEqual(list(qc.counts_to_probs({"01": 3, "10": 1}, 2)), [0, 3, 1, 0])

    @unittest.skipIf(HAVE_QISKIT, "Qiskit installed: the real cross-check runs instead")
    def test_missing_qiskit_is_a_skip_here_and_an_error_on_the_mac(self):
        code, rows = lines(qc.main, ["--here"])
        self.assertEqual((code, rows[0]["status"]), (0, "skipped"))
        self.assertEqual(lines(qc.main, [])[0], 2)

    @unittest.skipUnless(HAVE_QISKIT, "needs qiskit + qiskit-aer (pendingMac)")
    def test_qiskit_and_aer_agree_with_numpy(self):
        code, rows = lines(qc.main, [])
        self.assertEqual(code, 0, rows)


class Profile(unittest.TestCase):
    def test_budget_comes_from_the_track_profile(self):
        self.assertLess(_mac.profile(16)["budget_gb"], _mac.profile(64)["budget_gb"])


if __name__ == "__main__":
    unittest.main()
