"""Shared, cached sessions for the tests (one fake-model session per fault, built once per process)."""
import functools
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))

import claims  # noqa: E402
import registry  # noqa: E402
import run_project  # noqa: E402

A = {"lam": 0.8, "mu": 1.0}
B = {"lam": 0.8, "mu": 1.05}


@functools.lru_cache(maxsize=None)
def session(inject=None):
    reg = registry.Registry()
    pl, out = run_project.session(inject, False, reg)
    rows, published = claims.review(out["summary"], reg)
    return reg, pl, out, rows, published


def ab_facts(reg):
    exp = next(r for r in reg.records if r["kind"] == "experiment" and "verdict" in r["facts"])
    return exp["experiment_id"], {k: v["value"] for k, v in exp["facts"].items()}
