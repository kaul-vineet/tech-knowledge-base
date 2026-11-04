"""Shared test helper: puts the lab folder on sys.path, runs traffic phases with a fake clock and seeded faults."""
import functools
import os
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))

INJECT = os.environ.get("INJECT") or None        # INJECT=bypass / downgrade reproduces the faults in the seam tests


@functools.lru_cache(maxsize=None)
def context(inject=None):
    import run_project
    return run_project.collect(inject)


def phase_stats(variant, versions, required):
    """One traffic phase with a channel variant. Seam S3 and fitness F3 are evaluated while the phase's flags are set."""
    import crypto_registry as registry
    import fitness
    import fleet
    import seams
    registry.reset()
    registry.FLAGS.set("pq_required.messaging", required)
    try:
        servers = fleet.make_fleet(versions)
        stats = fleet.run_traffic(fleet.load_channel(variant), servers)
        stats.update(servers=servers, audit=list(registry.AUDIT), expected_offers=registry.expected_offers("messaging"),
                     s3=seams.s3_agility_to_wire(stats["tap"]),
                     f3=fitness.f3_registry_only(LAB / fleet.FOLDERS[variant] / "channel.py", stats["tap"]))
        return stats
    finally:
        registry.reset()
