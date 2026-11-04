"""Capstone plumbing: import the earlier labs instead of copying them. Each lab folder has its own helpers.py, so the
module cache is swapped around every load (the same loader as lab 20's harness.py)."""
import importlib.util, sys
from pathlib import Path

LABS = Path(__file__).resolve().parents[2]


def load(relpath, alias):
    path = LABS / relpath
    saved_path, saved = list(sys.path), {m: sys.modules.pop(m) for m in ("helpers", "analyze") if m in sys.modules}
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(alias, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.lab_helpers = sys.modules.get("helpers")
        return mod
    finally:
        sys.path[:] = saved_path
        for m in ("helpers", "analyze"):
            sys.modules.pop(m, None)
        sys.modules.update(saved)


SAGA = load("L300/14-sagas-compensation/solution_saga.py", "cap_saga")  # orchestrated saga + recover()
RAFT = load("L300/12-raft-replicated-log/solution_raft.py", "cap_raft")  # Raft with the election restriction
BACKPRESSURE = load("L300/16-backpressure-load-shedding/solution_backpressure.py", "cap_bp")  # bounded admission
TRACING = load("L300/15-distributed-tracing/solution_tracing.py", "cap_tracing")  # W3C traceparent parser
LINCHECK = load("L400/21-verifying-correctness/lincheck.py", "cap_lincheck")  # Porcupine-style checker
