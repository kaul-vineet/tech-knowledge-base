"""tryIt 2: what does one rotation cost as the group grows? Real hybrid welcomes for 3, 30 and 100 members (one
1,180-byte welcome each, plus the sealer's), then the per-epoch message limit for random 96-bit nonces."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import group_crypto as gc  # noqa: E402
from _kb import load  # noqa: E402

prob = load("prob", "prob_tools")
secret = os.urandom(32)
for n in (3, 30, 100):
    devices = [gc.Device(f"m{i}") for i in range(n)] + [gc.Device("svc")]
    entry = {"type": "epoch", "epoch": 2, "members": [d.name for d in devices[:-1]],
             "welcomes": {d.name: gc.welcome(d.key_package, secret, 2, d.name) for d in devices}}
    raw = sum(gc.welcome_bytes(w) for w in entry["welcomes"].values())
    print(f"{n:4} members: welcomes {raw:,} B raw, log entry {len(json.dumps(entry)):,} B JSON, x3 replicas")
q = prob.q_for_probability(2**-32, 2**96)
print(f"random 96-bit nonces: collision risk 2^-32 after {q:.3e} messages per epoch key "
      f"(NIST SP 800-38D caps random-IV use at 2^32 = {2**32:,})")
