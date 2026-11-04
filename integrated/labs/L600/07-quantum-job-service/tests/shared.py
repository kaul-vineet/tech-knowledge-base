"""Test helper: put the lab folder on sys.path and run each seeded load test once per process."""
import functools
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))

import loadtest  # noqa: E402
import scenarios  # noqa: E402


@functools.lru_cache(maxsize=None)
def load(fault=None, policy="floor+budget"):
    return loadtest.run(fault=fault, policy=policy)


@functools.lru_cache(maxsize=None)
def lease_lab(fault=None):
    return scenarios.lease_expiry(fault)
