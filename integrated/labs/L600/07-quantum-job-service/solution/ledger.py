"""Reference ledger: idempotent chunk attempts + per-attempt fencing tokens.

Each chunk slot is the distributed-systems L200 #7 FencedStorage (reused, not copied): a write REPLACES the value and
a write whose token is lower than the highest token seen is rejected. A chunk therefore holds exactly one attempt's
counts (its shots), however many attempts ran; attempts of one chunk use the same seed, so their counts are identical.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _kb import election  # noqa: E402
from jobstore import JobStore  # noqa: E402


class Ledger(JobStore):
    def new_slot(self):
        return election.FencedStorage(fencing=True)

    def write(self, slot, token, counts):
        return slot.write(token, counts)        # "accepted" or "REJECTED (token 3 < 7)"

    def read(self, slot):
        return slot.value
