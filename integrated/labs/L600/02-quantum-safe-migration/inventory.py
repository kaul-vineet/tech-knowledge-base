"""Milestone 3 - crypto inventory of the sample repo (code + config), one finding per algorithm use.

Python: quantum L400 #21's AST scanner (imports + aliases -> calls -> purpose), plus calls into crypto_registry, which
are reported as what the registry resolves to today. Config: nginx ssl_ecdh_curve, JSSE jdk.tls.namedGroups, JWS alg.
Every finding is mapped to a service from sample_repo/services.json; files nobody owns map to "unowned".
Known blind spot (failure lab + build task): modules loaded dynamically by name are invisible to this scanner.
"""
import ast
import json
import re
from pathlib import Path

import _kb  # noqa: F401
import crypto_registry as registry
import solution_scanner as l21  # quantum L400 #21: scan_python(path, rel) -> [{file, line, algorithm, usage}]

HERE = Path(__file__).resolve().parent
SERVICES = json.loads((HERE / "sample_repo" / "services.json").read_text(encoding="utf-8"))["services"]
GROUPS = {"x25519": "X25519", "x448": "X448", "prime256v1": "P-256", "secp256r1": "P-256", "secp384r1": "P-384",
          "x25519mlkem768": "X25519MLKEM768", "secp256r1mlkem768": "SecP256r1MLKEM768"}
JWS = {"RS": "RSA", "PS": "RSA-PSS", "ES": "ECDSA"}
CONFIG = [(re.compile(r"^\s*ssl_ecdh_curve\s+([^;#]+);"), "groups"),
          (re.compile(r"^\s*jdk\.tls\.namedGroups\s*=\s*(\S+)"), "groups"),
          (re.compile(r"^\s*signature_algorithm\s*:\s*(RS|PS|ES)(\d{3})\b"), "jws")]
REGISTRY_CALLS = {"kex_offers": "kex", "classic_fallback": "kex", "verifier": "sig", "signer": "sig", "aead": "aead"}
STAGES = ("before", "after")


def service_of(rel):
    owners = [(len(p), name) for name, s in SERVICES.items() for p in s["paths"] if rel.startswith(p + "/")]
    return max(owners)[1] if owners else "unowned"


def is_pq(algorithm):
    return "MLKEM" in algorithm or "ML-KEM" in algorithm or "ML-DSA" in algorithm


def scan_config(path, rel):
    found = []
    for no, text in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for rx, kind in CONFIG:
            m = rx.search(text)
            if not m:
                continue
            if kind == "groups":
                names = [GROUPS.get(g.strip().lower(), g.strip()) for g in re.split(r"[:,\s]+", m.group(1)) if g.strip()]
                found.append({"file": rel, "line": no, "algorithm": "ECDHE " + "/".join(names), "usage": "key-establishment"})
            else:
                found.append({"file": rel, "line": no, "algorithm": f"{JWS[m.group(1)]} (JWS {m.group(1)}{m.group(2)})",
                              "usage": "signature"})
    return found


def scan_registry_calls(path, rel):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    service = next((n.value.value for n in ast.walk(tree) if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant)
                    and any(isinstance(t, ast.Name) and t.id == "SERVICE" for t in n.targets)), service_of(rel))
    found = []
    for node in ast.walk(tree):
        f = getattr(node, "func", None)
        if isinstance(node, ast.Call) and isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) \
                and f.value.id == "registry" and f.attr in REGISTRY_CALLS:
            d = registry.describe(service, REGISTRY_CALLS[f.attr])
            found.append({"file": rel, "line": node.lineno, "algorithm": d["algorithm"], "usage": d["usage"],
                          "classical_fallback": d["classical_fallback"]})
    return found


def scan_python(path, rel):
    return l21.scan_python(path, rel) + scan_registry_calls(path, rel)


def scan(stage="before", messaging="migrated/messaging", python_scanner=None):
    """stage 'before' = the repo as found; 'after' = sample_repo's messaging replaced by the folder `messaging`."""
    python_scanner = python_scanner or scan_python
    roots = [HERE / "sample_repo"] + ([HERE / messaging] if stage == "after" else [])
    found = []
    for root in roots:
        for path in sorted(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
            rel = path.relative_to(HERE).as_posix()
            if stage != "before" and rel.startswith("sample_repo/services/messaging/"):
                continue
            if path.suffix == ".py":
                found += python_scanner(path, rel)
            elif path.suffix in (".conf", ".properties", ".yaml", ".yml", ".toml"):
                found += scan_config(path, rel)
    for f in found:
        f.update(service=service_of(f["file"]), pq=is_pq(f["algorithm"]))
        f.setdefault("classical_fallback", False)
    return sorted(found, key=lambda f: (f["file"], f["line"], f["algorithm"]))


def score(found, expected):
    key = lambda f: (f["file"], f["line"], f["algorithm"], f["usage"])  # noqa: E731
    got, want = {key(f) for f in found}, {key(f) for f in expected}
    tp = len(got & want)
    return {"recall": round(tp / len(want), 3), "precision": round(tp / len(got), 3) if got else 0.0,
            "missing": sorted(want - got), "extra": sorted(got - want)}


if __name__ == "__main__":
    for stage in STAGES:
        for f in scan(stage):
            print(json.dumps({"stage": stage, **f}))
