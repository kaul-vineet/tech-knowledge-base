"""Fitness function for crypto agility: no hard-coded algorithm outside the registry (static AST check).
A violation is (1) importing a concrete primitive module, (2) naming a concrete algorithm class, or
(3) a string literal equal to a registered algorithm id, in any module that is not allow-listed.
Usage: python agility_lint.py [files or folders ...]   (exit code 1 if any violation)"""
import ast
import re
import sys
from pathlib import Path

PRIMITIVE_MODULES = re.compile(r"^cryptography\.hazmat\.primitives\.(ciphers|asymmetric|hpke)(\.|$)")
ALGORITHM_NAMES = re.compile(r"^(AESGCM|AESGCMSIV|AESOCB3|AESSIV|AESCCM|ChaCha20Poly1305|Ed25519\w*|Ed448\w*"
                             r"|X25519\w*|X448\w*|MLDSA\d+\w*|MLKEM\d+\w*|ed25519|ed448|x25519|mldsa|mlkem)$")
ALLOWED_FILES = {"registry.py", "agility_lint.py", "try_it.py", "tool_check.py", "measure_options.py"}  # + test_*.py


def _ids():
    try:
        import registry
        return set(registry.REGISTRY)
    except ImportError:
        return {"A256GCM", "C20P1305", "Ed25519", "ML-DSA-65"}


def scan_source(source: str, name: str = "<string>", ids=None) -> list:
    ids = ids if ids is not None else _ids()
    found = []
    for node in ast.walk(ast.parse(source, name)):
        line = getattr(node, "lineno", 0)
        if isinstance(node, ast.ImportFrom) and node.module and PRIMITIVE_MODULES.match(node.module):
            found.append((name, line, f"imports {node.module}"))
        elif isinstance(node, ast.Import):
            found += [(name, line, f"imports {a.name}") for a in node.names if PRIMITIVE_MODULES.match(a.name)]
        elif isinstance(node, ast.Name) and ALGORITHM_NAMES.match(node.id):
            found.append((name, line, f"names algorithm {node.id}"))
        elif isinstance(node, ast.Attribute) and ALGORITHM_NAMES.match(node.attr):
            found.append((name, line, f"names algorithm {node.attr}"))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in ids:
            found.append((name, line, f"hard-codes algorithm id {node.value!r}"))
    return found


def scan(paths) -> list:
    files = []
    for p in map(Path, paths):
        files += sorted(p.rglob("*.py")) if p.is_dir() else [p]
    found = []
    for f in files:
        if f.name in ALLOWED_FILES or f.name.startswith("test_") or "__pycache__" in f.parts:
            continue
        found += scan_source(f.read_text(encoding="utf-8"), f.as_posix())
    return found


if __name__ == "__main__":
    violations = scan(sys.argv[1:] or [Path(__file__).resolve().parent])
    for file, line, why in violations:
        print(f"{file}:{line}: {why}")
    print(f"agility_lint: {len(violations)} violation(s)")
    sys.exit(1 if violations else 0)
