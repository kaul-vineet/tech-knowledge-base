"""Shared fixtures: the lab folder on sys.path and ONE cached seeded run per process (the stub boards are slow
to load on network storage; the simulation itself takes a few seconds of CPU)."""
import functools
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))

import fleet_sim  # noqa: E402


@functools.lru_cache(maxsize=None)
def run(seed=4, inject=None, hours=12, sync_every=None, firmware="node.py", radio_partition=(120, 300)):
    return fleet_sim.run(seed=seed, inject=inject, hours=hours, sync_every=sync_every, firmware=firmware,
                         radio_partition=radio_partition)
