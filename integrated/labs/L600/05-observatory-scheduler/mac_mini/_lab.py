"""Path helper for the Mac mini scripts: the lab folder (one up) and the shared track scripts (mac_profile.py).

build() makes the night once per process (the same call as run_project.py: seed 2026, no fault)."""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
KB = LAB.parents[3]
TRACK = KB / "integrated" / "mac-mini" / "scripts"
for p in (LAB, TRACK):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def runs_dir(arg=None):
    """Where JSONL results go: --out, else $KB_RUNS_DIR, else ~/kb-runs (the nightly job's folder)."""
    d = Path(arg) if arg else Path(os.environ.get("KB_RUNS_DIR") or Path.home() / "kb-runs")
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_jsonl(path, rows):
    import json
    path = Path(path)
    path.unlink(missing_ok=True)  # the storage mount breaks in-place overwrite: delete, then write
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return path


_NIGHT = {}


def build(seed=2026):
    if seed not in _NIGHT:
        import scheduler
        _NIGHT[seed] = scheduler.build(seed=seed)
    return _NIGHT[seed]
