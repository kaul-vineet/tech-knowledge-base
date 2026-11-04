"""Build-task solution for lab 21: an AST-based crypto inventory. Run: python solution_scanner.py

Python files: resolve imports from cryptography's asymmetric/aead modules (aliases included), then find the CALLS
that use an algorithm and classify them by purpose. Config files: match known key/group settings, skip comments.
Words in docstrings or comments are never findings.
"""
import ast
import json
import re

import pqc_lab as lab

MODULES = {"rsa", "ec", "x25519", "x448", "ed25519", "ed448", "dh", "dsa", "padding", "aead"}
RULES = {  # canonical call -> (algorithm, usage); {curve} / {bits} filled from the same file
    "x25519.X25519PrivateKey.generate": ("X25519", "key-establishment"),
    "x448.X448PrivateKey.generate": ("X448", "key-establishment"),
    "ec.ECDH": ("ECDH {curve}", "key-establishment"),
    "ec.ECDSA": ("ECDSA {curve}", "signature"),
    "ed25519.Ed25519PrivateKey.generate": ("Ed25519", "signature"),
    "dh.generate_parameters": ("FFDH", "key-establishment"),
    "dsa.generate_private_key": ("DSA", "signature"),
    "rsa.generate_private_key": ("RSA-{bits}", "{rsa_usage}"),
    "aead.AESGCM": ("AES-GCM", "symmetric"),
}
CURVES = {"SECP256R1": "P-256", "SECP384R1": "P-384", "SECP521R1": "P-521"}
CONFIG = [(re.compile(r"rsa-(\d+)", re.I), "RSA-{0}", "signature"),
          (re.compile(r"groups\s*=.*x25519.*secp256r1", re.I), "ECDHE X25519/P-256", "key-establishment")]


def aliases(tree):
    """Local name -> canonical 'module' or 'module.Name' for cryptography imports."""
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("cryptography.hazmat.primitives"):
            last = node.module.rsplit(".", 1)[-1]
            for a in node.names:
                if a.name in MODULES:
                    out[a.asname or a.name] = a.name                      # from ...asymmetric import ec as curves
                elif last in MODULES:
                    out[a.asname or a.name] = f"{last}.{a.name}"          # from ...asymmetric.ec import ECDH
    return out


def dotted(node, names):
    if isinstance(node, ast.Name):
        return names.get(node.id)
    if isinstance(node, ast.Attribute):
        base = dotted(node.value, names)
        return f"{base}.{node.attr}" if base else None
    return None


def scan_python(path, rel):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = aliases(tree)
    calls = [(dotted(n.func, names), n) for n in ast.walk(tree) if isinstance(n, ast.Call)]
    curve = next((CURVES[c.split(".")[-1]] for c, _ in calls if c and c.split(".")[-1] in CURVES), "")
    rsa_usage = "key-establishment" if any(c == "padding.OAEP" for c, _ in calls) else "signature"
    found = []
    for canon, node in calls:
        if canon in RULES:
            algo, usage = RULES[canon]
            bits = next((k.value.value for k in node.keywords if k.arg == "key_size"), "?")
            found.append({"file": rel, "line": node.lineno, "algorithm": algo.format(curve=curve, bits=bits).strip(),
                          "usage": usage.format(rsa_usage=rsa_usage)})
    return found


def scan_config(path, rel):
    found = []
    for no, text in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if text.lstrip().startswith("#"):
            continue
        for rx, algo, usage in CONFIG:
            m = rx.search(text)
            if m:
                found.append({"file": rel, "line": no, "algorithm": algo.format(*m.groups()), "usage": usage})
    return found


def scan(root=lab.APP):
    found = []
    for path in sorted(p for p in root.rglob("*") if p.suffix in (".py", ".toml", ".yaml", ".yml", ".conf")):
        rel = path.relative_to(lab.HERE).as_posix()
        found += scan_python(path, rel) if path.suffix == ".py" else scan_config(path, rel)
    return sorted(found, key=lambda f: (f["file"], f["line"]))


if __name__ == "__main__":
    inventory = scan()
    print(json.dumps({"scanner": "ast", "findings": len(inventory)}))
    for step in lab.plan(inventory):
        print(json.dumps(step))
