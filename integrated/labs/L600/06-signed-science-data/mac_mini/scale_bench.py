"""Experiment 2 - how far does the release pipeline scale on THIS machine? Merkle build + sign + verify for big catalogues.

python mac_mini/scale_bench.py --here                 10,000 rows (seconds; proves the script and the tree maths)
python mac_mini/scale_bench.py --rows 1e5 1e6 1e7     the Mac mini run (1e7 rows needs several GB: see the wall line)
python mac_mini/scale_bench.py --rows 1e7 --streaming root only, O(log n) memory (no proofs from memory)

Per size: rows -> science.process (the project's processing step) -> JCS bytes per row (canonical.dumps) -> RFC 9162
leaf hashes -> tree -> root signed by Ed25519 + ML-DSA-65 (trust.sign, the publisher's algorithms) -> verified ->
100 inclusion proofs checked with merkle.verify_inclusion. Throughput in rows/s per step; memory as peak RSS growth
per row. The tree here is built bottom-up (pairs, an odd last node moves up unchanged), which is the same tree as
merkle.mth's recursive RFC 9162 definition (checked against it for every size <= 20,000 and in the tests);
merkle.mth itself copies list slices at every level, fine for 20 leaves, not for 10 million.
"""
import argparse
import random
import resource
import sys
import time

import numpy as np

import _mac
import canonical as C
import merkle
import science
import trust

CROSSCHECK_MAX = 20000


CHUNK = 100_000


def synthetic_rows(n, seed=21):
    """Gaia-like astrometry rows, SYNTHETIC (like astronomy L400 #21 inputs.rows): chunks of CHUNK rows, chunk k drawn
    from default_rng([seed, k]), so the in-memory and the streaming runs see exactly the same rows."""
    for k, start in enumerate(range(0, n, CHUNK)):
        m = min(CHUNK, n - start)
        rng = np.random.default_rng([seed, k])
        plx, err = rng.uniform(0.2, 50.0, m), rng.uniform(0.02, 0.6, m)
        ra, dec, tmag = rng.uniform(0, 360, m), rng.uniform(-90, 90, m), rng.uniform(4, 16, m)
        yield [{"source_id": 4_000_000_000_000_000 + start + i, "ra": round(float(ra[i]), 6),
                "dec": round(float(dec[i]), 6), "parallax": round(float(plx[i]), 4),
                "parallax_error": round(float(err[i]), 4), "tmag": round(float(tmag[i]), 3)} for i in range(m)]


def build_levels(leaf_hashes):
    levels = [leaf_hashes]
    while len(levels[-1]) > 1:
        cur = levels[-1]
        nxt = [merkle.node_hash(cur[i], cur[i + 1]) for i in range(0, len(cur) - 1, 2)]
        if len(cur) % 2:
            nxt.append(cur[-1])          # odd last node: carried up unchanged (RFC 9162 split rule, bottom-up)
        levels.append(nxt)
    return levels


def proof(levels, m):
    path = []
    for lvl in levels[:-1]:
        if m ^ 1 < len(lvl):
            path.append(lvl[m ^ 1])
        m >>= 1
    return path


def stream_push(stack, leaf_hashes):
    """Binary-counter stack of perfect subtrees: O(log n) hashes in memory, whatever n is."""
    for h in leaf_hashes:
        stack.append((0, h))
        while len(stack) > 1 and stack[-1][0] == stack[-2][0]:
            (k, right), (_, left) = stack.pop(), stack.pop()
            stack.append((k + 1, merkle.node_hash(left, right)))
    return stack


def stream_fold(stack):
    root = stack[-1][1]
    for _, left in reversed(stack[:-1]):  # smaller subtrees sit on the right: fold right to left
        root = merkle.node_hash(left, root)
    return root


def stream_root(leaf_hashes):
    return stream_fold(stream_push([], leaf_hashes))


def rss():
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r if sys.platform == "darwin" else r * 1024   # macOS: bytes; Linux: KiB


def bench(n, streaming=False, seed=21):
    """streaming=False keeps every leaf and every tree level (proofs from memory); True keeps only the O(log n) stack."""
    t = dict.fromkeys(("process", "canonicalise", "leaf_hash", "tree"), 0.0)
    out, rss0, size = {"rows": n, "streaming": streaming}, rss(), 0
    leaves, hashes, stack = [], [], []
    for chunk in synthetic_rows(n, seed):
        s = time.perf_counter()
        rows = science.process(chunk)
        t["process"] += time.perf_counter() - s
        s = time.perf_counter()
        part = [C.dumps(r) for r in rows]
        t["canonicalise"] += time.perf_counter() - s
        size += sum(map(len, part))
        s = time.perf_counter()
        hs = [merkle.leaf_hash(x) for x in part]
        t["leaf_hash"] += time.perf_counter() - s
        if streaming:
            s = time.perf_counter()
            stack = stream_push(stack, hs)
            t["tree"] += time.perf_counter() - s
        else:
            leaves += part
            hashes += hs
    s = time.perf_counter()
    if streaming:
        root, levels = stream_fold(stack), None
    else:
        levels = build_levels(hashes)
        root = levels[-1][0]
    t["tree"] += time.perf_counter() - s
    out["bytes_per_row_jcs"] = round(size / n, 1)
    signers = [trust.Signer("Ed25519", "bench-release"), trust.Signer("ML-DSA-65", "bench-release")]
    s = time.perf_counter()
    env = trust.sign({"_type": "release", "rows": n, "merkle_root": root.hex()}, signers)
    sign_ms = (time.perf_counter() - s) * 1000
    keys = {x.kid: x.entry() for x in signers}
    s = time.perf_counter()
    ok_sig = len(trust.valid_kids(env, keys)) == 2
    verify_ms = (time.perf_counter() - s) * 1000
    proofs_ok, proof_us = None, None
    if levels is not None:
        rng = random.Random(seed)
        picks = [rng.randrange(n) for _ in range(100)]
        s = time.perf_counter()
        proofs_ok = all(merkle.verify_inclusion(leaves[m], m, n, proof(levels, m), root) for m in picks)
        proof_us = round((time.perf_counter() - s) / len(picks) * 1e6, 1)
        if n <= CROSSCHECK_MAX:
            out["same_root_as_merkle_mth"] = merkle.mth(leaves) == root and stream_root(hashes) == root
    grow = rss() - rss0
    out.update({"root": root.hex()[:16], "rows_per_s": {k: round(n / v) for k, v in t.items() if v > 0},
                "sign_ms": round(sign_ms, 2), "verify_ms": round(verify_ms, 2), "proof_verify_us": proof_us,
                "signatures_valid": ok_sig, "proofs_valid": proofs_ok, "proof_hashes_max": (n - 1).bit_length(),
                "rss_growth_B": grow, "rss_B_per_row": round(grow / n, 1) if grow > 0 else None,
                "seconds_total": round(sum(t.values()), 2)})
    return out


def wall(bytes_per_row):
    prof = _mac.mac_profile()
    return {g: int(prof.recommend(prof.ram_from_gib(g))["budget_gb"] * 1e9 // bytes_per_row) for g in (16, 24, 32, 64)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--here", action="store_true")
    ap.add_argument("--rows", type=float, nargs="+", default=[1e5, 1e6, 1e7])
    ap.add_argument("--streaming", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    sizes = [10000] if a.here else [int(x) for x in a.rows]
    m = _mac.mac_profile().detect()
    _mac.emit({"experiment": "06 Merkle scale benchmark", "mode": "here" if a.here else "mac", "system": m["system"],
               "arch": m["arch"], "sizes": sizes, "at": _mac.stamp()}, a.out)
    ok, last = True, None
    for n in sizes:
        last = bench(n, a.streaming)
        ok &= last["signatures_valid"] and last["proofs_valid"] is not False and last.get("same_root_as_merkle_mth", True)
        _mac.emit(last, a.out)
    if last and last["rss_B_per_row"] and not a.streaming:
        _mac.emit({"wall": "max rows in memory (in-memory tree + leaves)", "rss_B_per_row": last["rss_B_per_row"],
                   "measured_at_rows": last["rows"], "reliable": last["rows"] >= 100_000,  # start-up dominates below
                   "max_rows_by_ram_GB": wall(last["rss_B_per_row"]),
                   "reading": "max_rows below your catalogue size -> build the tree streaming (stream_root, O(log n))"
                              " and keep leaves/levels on disk; proofs then read from disk"}, a.out)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
