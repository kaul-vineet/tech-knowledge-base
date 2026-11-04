"""Plumbing for lab 20 (not the lesson's concept): load the L300 labs by path (each has its own helpers.py, so the
module cache is swapped around every load), a stable cohort hash for blast-radius control, and JSON lines."""
import hashlib, importlib.util, json, sys
from pathlib import Path

L300 = Path(__file__).resolve().parents[2] / "L300"


def load(relpath, alias):
    """Import labs/L300/<relpath> as `alias` with ITS OWN helpers.py, without disturbing ours."""
    path = L300 / relpath
    saved_path, saved_helpers = list(sys.path), sys.modules.pop("helpers", None)
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(alias, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.lab_helpers = sys.modules.get("helpers")  # keep a handle (Raft's Cluster, the saga's Crash)
        return mod
    finally:
        sys.path[:] = saved_path
        sys.modules.pop("helpers", None)
        if saved_helpers is not None:
            sys.modules["helpers"] = saved_helpers


def cohort(keys, pct, salt):
    """Stable experiment group: exactly floor(pct% of keys), chosen by a salted hash - the same orders every run."""
    ranked = sorted(keys, key=lambda k: hashlib.sha256(f"{salt}:{k}".encode()).hexdigest())
    return set(ranked[:int(len(keys) * pct / 100)])


def jsonl(rows):
    return [json.dumps(r, sort_keys=True) for r in rows]
