"""Tests for project 06's Mac mini scripts at sandbox size (python -m unittest discover -s mac_mini/tests).
Tree maths against the lab's RFC 9162 merkle.py, the HTTP mirrors (real processes) with and without the seeded
float-format fault, and the cross-language JCS check (skipped if `node` is absent)."""
import contextlib
import io
import json
import shutil
import sys
import unittest
from pathlib import Path

MAC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MAC))
import http_world  # noqa: E402
import jcs_crosscheck  # noqa: E402
import merkle  # noqa: E402
import scale_bench as sb  # noqa: E402


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


class Tree(unittest.TestCase):
    def test_bottom_up_and_streaming_trees_equal_rfc9162_mth(self):
        for n in list(range(1, 70)) + [127, 128, 129, 1000]:
            leaves = [f"leaf {i}".encode() for i in range(n)]
            hashes = [merkle.leaf_hash(x) for x in leaves]
            root = sb.build_levels(hashes)[-1][0]
            self.assertEqual(root, merkle.mth(leaves), n)
            self.assertEqual(sb.stream_root(hashes), root, n)

    def test_every_inclusion_proof_verifies_with_the_lab_verifier(self):
        for n in range(1, 40):
            leaves = [f"row {i}".encode() for i in range(n)]
            levels = sb.build_levels([merkle.leaf_hash(x) for x in leaves])
            for m in range(n):
                self.assertTrue(merkle.verify_inclusion(leaves[m], m, n, sb.proof(levels, m), levels[-1][0]), (n, m))
                self.assertEqual(sb.proof(levels, m), merkle.inclusion_proof(m, leaves))

    def test_bench_in_memory_and_streaming_agree(self):
        a, b = quiet(sb.bench, 2500), quiet(sb.bench, 2500, True)
        self.assertTrue(a["proofs_valid"] and a["signatures_valid"] and a["same_root_as_merkle_mth"])
        self.assertEqual(a["root"], b["root"])
        self.assertEqual(a["proof_hashes_max"], 12)


class Mirrors(unittest.TestCase):
    def go(self, inject):
        d = MAC / "runs" / f"test-http-{inject}"
        shutil.rmtree(d, ignore_errors=True)
        try:
            return quiet(http_world.run, d, mirrors=3, releases=2, seed=6, inject=inject)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_http_mirrors_converge_and_verify(self):
        _, h1, h2, h3 = self.go(None)
        self.assertTrue(h1["pass"] and h2["pass"] and h3["pass"], (h1, h2, h3))

    def test_float_format_mirror_breaks_convergence_and_verification(self):
        _, h1, h2, _ = self.go("float-format")
        self.assertFalse(h1["pass"])
        self.assertFalse(h2["verified"]["m2"])
        self.assertTrue(h2["verified"]["m0"])


class Jcs(unittest.TestCase):
    def test_rfc8785_sample_in_python(self):
        sample = next(v for v in jcs_crosscheck.vectors() if v["id"] == "rfc8785-sample")
        self.assertEqual(jcs_crosscheck.C.dumps(sample["value"]), jcs_crosscheck.RFC8785_SAMPLE_OUT.encode())

    @unittest.skipIf(shutil.which("node") is None, "node not installed")
    def test_node_builtin_recipe_gives_identical_bytes(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = jcs_crosscheck.main(["--here"])
        rows = [json.loads(x) for x in buf.getvalue().splitlines()]
        self.assertEqual(code, 0, rows)
        self.assertGreater(rows[-1]["platform_dumps_vectors_that_differ"], 0)


if __name__ == "__main__":
    unittest.main()
