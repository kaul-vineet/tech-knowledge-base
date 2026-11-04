"""L600 #06 - a verifiable, replicated science-data release pipeline (astronomy x cryptography x distributed systems).

python run_project.py                       -> scorecard as JSON lines; exit 0 only if every check passes
python run_project.py --inject float-format -> the failure lab: mirror m2 re-serialises JSON with '%.17g' doubles
other seeded faults: drop-old-key (rotation forgets old keys), no-freshness (client skips expiry/version checks),
licence-drop (builder uses astronomy L400 #21's unfixed licence function)

Flow: science.py (process) -> publisher.py (licence gate, files, Merkle manifest, Ed25519 + ML-DSA-65 signatures,
transparency log, timestamp) -> mirrors.py (upload to m0, anti-entropy to m1-m3) -> client.py (verify everything).
world.py runs that story once; checks.py holds every milestone, seam and fitness check (tests call the same code).
"""
import argparse
import json
import sys
import time

import checks
from world import World

FAULTS = ["float-format", "drop-old-key", "no-freshness", "licence-drop"]


def diagnose(w):
    """Failure-lab helper: show the first differing bytes of the catalogue between m0 and m2."""
    a = w.mirrors[0].objects.get("releases/v1/catalogue.json", b"")
    b = w.mirrors[2].objects.get("releases/v1/catalogue.json", b"")
    i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), None)
    if i is None:
        return None
    start = a.rfind(b",", 0, i) + 1
    return {"m0": a[start:start + 34].decode(), "m2": b[start:start + 34].decode(), "offset": i}


def main(inject=None, only=None):
    t0 = time.perf_counter()
    w = World(inject)
    results = []
    for kind, cid, title, fn in checks.CHECKS:
        if only and cid not in only:
            continue
        ok, detail = fn(w)
        results.append(ok)
        print(json.dumps({"kind": kind, "id": cid, "title": title, "pass": ok, **detail}))
    if inject == "float-format":
        print(json.dumps({"kind": "diagnose", "first_difference_v1_catalogue": diagnose(w)}))
    print(json.dumps({"scorecard": "PASS" if all(results) else "FAIL", "passed": sum(results), "total": len(results),
                      "inject": inject, "seconds": round(time.perf_counter() - t0, 1)}))
    return all(results)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--inject", choices=FAULTS, help="reproduce a seeded fault")
    ap.add_argument("--only", nargs="*", help="run only these check ids, e.g. --only S1 F2")
    args = ap.parse_args()
    sys.exit(0 if main(args.inject, args.only) else 1)
