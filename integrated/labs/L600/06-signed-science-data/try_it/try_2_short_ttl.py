"""tryIt 2: shorten the timestamp lifetime (TTL) to 120 s - 'fresher is safer'? The publisher signs a timestamp only
when it publishes; the client checks 300 s later, after gossip finished. Predict how many mirrors it can use."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import publisher as P  # noqa: E402
import world as W  # noqa: E402

for ttl in (3600, 120):
    P.TTL = ttl
    w = W.World()
    usable, why = [], ""
    for m in w.mirrors:
        try:
            w.client().fetch(m, w.pub.log, w.now + 300)
            usable.append(m.name)
        except P.trust.Rejected as e:
            why = str(e).split(": ", 1)[1]
    print(f"2) TTL {ttl:>4} s: usable mirrors {usable or 'none'}" + (f" | {why}" if why else ""))
