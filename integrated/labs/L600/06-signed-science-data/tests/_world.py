"""Shared fixture: put the lab folder on sys.path and build each seeded World once per test process (it is
deterministic, so sharing it between test files is safe)."""
import functools
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))

from world import World  # noqa: E402


@functools.lru_cache(maxsize=None)
def world(inject=None):
    return World(inject)
