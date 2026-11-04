"""Experiment 3 - do two languages produce the SAME signed bytes? canonical.dumps (Python) vs JavaScript (Node).

python mac_mini/jcs_crosscheck.py --here                     Node's built-in recipe only (needs `node`; skips if absent)
cd mac_mini/jcs_node && npm install && cd ../..              Mac mini: add the npm package canonicalize 5.1.0
python mac_mini/jcs_crosscheck.py                            both implementations

Vectors: the four release catalogues (science.catalogue v1-v4, real processed rows), one release manifest, the
RFC 8785 sample from the JCS reference repository (with its published expected output), number edge cases
(-0, 1e21, 1e-7, 5e-324, max double, 0.1 + 0.2 ...) and key-ordering cases (UTF-16 code-unit order: emoji vs U+FB01).
Each vector is handed to Node as NON-canonical text (indented, keys reversed); Node parses and canonicalises it; the
bytes must equal Python's canonical.dumps of the same value. The failure lab's platform_dumps bytes are compared too:
they must DIFFER (that is why a mirror that re-serialises breaks every signature).
"""
import argparse
import json
import shutil
import subprocess
import sys
import time

import _mac
import canonical as C
import publisher as P
import science

NODE_DIR = _mac.HERE / "jcs_node"
RFC8785_SAMPLE_IN = ('{"numbers": [333333333.33333329, 1E30, 4.50, 2e-3, 0.000000000000000000000000001], '
                     '"string": "\\u20ac$\\u000F\\u000aA\'\\u0042\\u0022\\u005c\\\\\\"\\/", "literals": [null, true, false]}')
RFC8785_SAMPLE_OUT = ('{"literals":[null,true,false],"numbers":[333333333.3333333,1e+30,4.5,0.002,1e-27],'
                      '"string":"\u20ac$\\u000f\\nA\'B\\"\\\\\\\\\\"/"}')


def _reverse_keys(v):
    if isinstance(v, dict):
        return {k: _reverse_keys(v[k]) for k in reversed(list(v))}
    if isinstance(v, list):
        return [_reverse_keys(x) for x in v]
    return v


def vectors():
    objs = {f"catalogue-v{v}": science.catalogue(v) for v in (1, 2, 3, 4)}
    files = P.build_files(1)
    objs["release-manifest-v1"] = P.manifest(1, 0, files)
    objs["numbers"] = {"neg_zero": -0.0, "big": 1e21, "small": 1e-7, "tiny": 5e-324, "max": 1.7976931348623157e308,
                       "third": 333333333.3333333, "sum": 0.1 + 0.2, "int": 100, "e300": 1e300, "half": 4.5}
    objs["key-order"] = {"\u20ac": 1, "\r": 2, "\u00f6": 3, "\U0001F600": 4, "\ufb01": 5, "a": 6, "A": 7, "": 8}
    out = [{"id": k, "text": json.dumps(_reverse_keys(v), indent=1), "value": v} for k, v in objs.items()]
    out.append({"id": "rfc8785-sample", "text": RFC8785_SAMPLE_IN, "value": json.loads(RFC8785_SAMPLE_IN)})
    return out


def run_node(vecs, impl, folder):
    path = folder / "vectors.json"
    path.write_text(json.dumps([{"id": v["id"], "text": v["text"]} for v in vecs]), encoding="utf-8")
    res = subprocess.run(["node", str(NODE_DIR / "jcs_check.mjs"), str(path), impl], capture_output=True, text=True,
                         timeout=120)
    if res.returncode:
        raise RuntimeError(res.stderr[-600:])
    return {r["id"]: bytes.fromhex(r["hex"]) for r in map(json.loads, res.stdout.splitlines())}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--here", action="store_true", help="built-in recipe only")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    vecs = vectors()
    py = {v["id"]: C.dumps(v["value"]) for v in vecs}
    sample_ok = py["rfc8785-sample"] == RFC8785_SAMPLE_OUT.encode("utf-8")
    _mac.emit({"check": "python canonical.dumps reproduces the published RFC 8785 sample", "pass": sample_ok}, a.out)
    if shutil.which("node") is None:
        _mac.emit({"jcs": "skipped", "reason": "node not found", "install": "brew install node@24 (see WORKSTATION-SETUP)"},
                  a.out)
        return 0 if a.here and sample_ok else 2
    impls = ["builtin"]
    if not a.here:
        if (NODE_DIR / "node_modules" / "canonicalize").exists():
            impls.append("canonicalize")
        else:
            _mac.emit({"jcs": "canonicalize package not installed", "install": "cd mac_mini/jcs_node && npm install"}, a.out)
    folder = _mac.HERE / "runs" / f"{time.strftime('%Y%m%d-%H%M%S')}-jcs"
    folder.mkdir(parents=True, exist_ok=True)
    ok = sample_ok
    try:
        version = subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip()
        for impl in impls:
            js = run_node(vecs, impl, folder)
            same = {k: js.get(k) == b for k, b in py.items()}
            platform_differs = sum(C.platform_dumps(v["value"]) != js.get(v["id"]) for v in vecs)
            ok &= all(same.values())
            _mac.emit({"cross_language": f"python canonical.dumps vs node {version} {impl}", "vectors": len(vecs),
                       "identical": sum(same.values()), "different": sorted(k for k, s in same.items() if not s),
                       "platform_dumps_vectors_that_differ": platform_differs, "pass": all(same.values())}, a.out)
    finally:
        shutil.rmtree(folder, ignore_errors=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
