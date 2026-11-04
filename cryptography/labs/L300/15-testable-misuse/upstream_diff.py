"""Provenance check for the vendored Wycheproof cases: is every case present, byte for byte, in upstream C2SP/wycheproof?
Offline (default): prints the SHA-256 of each vendored subset. With --upstream DIR (the testvectors_v1/ folder of a
checkout, e.g. `git clone --depth 1 https://github.com/C2SP/wycheproof.git`) it finds each vendored case by content
(inputs + expected result, not by tcId) and exits 1 if any case is missing or disagrees. CI runs it (job wycheproof-upstream)."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

VECTORS = Path(__file__).resolve().parent / "vectors"
# vendored subset -> (upstream file in testvectors_v1/, fields that identify a case)
PAIRS = {
    "aes_gcm_subset.json": ("aes_gcm_test.json", ("key", "iv", "aad", "msg", "ct", "tag")),
    "ed25519_subset.json": ("ed25519_test.json", ("pk", "msg", "sig")),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cases(doc: dict, fields: tuple):
    for g in doc["testGroups"]:
        pk = g.get("publicKey", {}).get("pk", "")
        for t in g["tests"]:
            row = {**t, "pk": pk}
            yield tuple(str(row.get(f, "")).lower() for f in fields), t


def compare(vendored: dict, upstream: dict, fields: tuple) -> list:
    """One row per vendored case: (our tcId, upstream tcId or None, verdict)."""
    index = dict(cases(upstream, fields))
    rows = []
    for key, t in cases(vendored, fields):
        u = index.get(key)
        if u is None:
            rows.append((t["tcId"], None, "MISSING upstream"))
        elif u["result"] != t["result"]:
            rows.append((t["tcId"], u["tcId"], f"result differs: ours {t['result']}, upstream {u['result']}"))
        else:
            rows.append((t["tcId"], u["tcId"], "match" if u["tcId"] == t["tcId"] else f"match (upstream tcId {u['tcId']})"))
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--upstream", type=Path, help="path to an upstream testvectors_v1/ folder")
    ap.add_argument("--ref", default="unknown", help="upstream commit (and date) to print in the report")
    args = ap.parse_args(argv)
    for ours in PAIRS:
        print(f"vendored {ours:<20} sha256 {sha256(VECTORS / ours)}")
    if args.upstream is None:
        print("offline: no upstream folder given, nothing compared (see README: 'Check the provenance yourself')")
        return 0
    bad = 0
    print("upstream ref:", args.ref)
    for ours, (theirs, fields) in PAIRS.items():
        path = args.upstream / theirs
        rows = compare(json.loads((VECTORS / ours).read_text(encoding="utf-8")),
                       json.loads(path.read_text(encoding="utf-8")), fields)
        ok = sum(r[2].startswith("match") for r in rows)
        bad += len(rows) - ok
        print(f"upstream {theirs:<20} sha256 {sha256(path)} | {ok}/{len(rows)} vendored cases found verbatim")
        for tc, utc, verdict in rows:
            if verdict != "match":
                print(f"  tcId {tc}: {verdict}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
