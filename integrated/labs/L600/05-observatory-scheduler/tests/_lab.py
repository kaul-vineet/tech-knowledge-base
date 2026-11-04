"""Puts the lab folder on sys.path and builds the night once per test process (fault from SCHED_FAULT, if set)."""
import sys
from functools import lru_cache
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))


@lru_cache(maxsize=None)
def night(seed=2026):
    import scheduler
    return scheduler.build(seed=seed)
