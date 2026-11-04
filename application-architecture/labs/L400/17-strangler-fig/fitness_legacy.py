"""Fitness function (lesson 17): no NEW code calls the legacy module. Run: python fitness_legacy.py (exit 1 = fail)

ast lists every import of legacy_monolith; callers not on the baseline (legacy_callers.json) fail the build.
The baseline is a ratchet: it may shrink as callers migrate, never grow. Same idea as an import-linter
'forbidden' contract with ignore_imports for the known callers.
"""
import ast
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent


def legacy_callers(folder=HERE, module="legacy_monolith"):
    callers = set()
    for path in sorted(folder.rglob("*.py")):
        parts = path.relative_to(folder).parts
        if path.stem == module or "solution" in parts or any(p.startswith(".") for p in parts[:-1]):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
            if any(n.split(".")[0] == module for n in names):
                callers.add(path.relative_to(folder).as_posix())
    return callers


def gate(folder=HERE, baseline=HERE / "legacy_callers.json"):
    allowed = set(json.loads(baseline.read_text(encoding="utf-8"))["allowed"])
    found = legacy_callers(folder)
    new, gone = sorted(found - allowed), sorted(allowed - found)
    return {"gate": "no-new-legacy-callers", "ok": not new, "value": {"new": new, "migrated": gone,
            "callers": len(found)}, "budget": f"<= {len(allowed)} known callers, no new ones"}


if __name__ == "__main__":
    result = gate()
    print(json.dumps(result, sort_keys=True))
    sys.exit(0 if result["ok"] else 1)
