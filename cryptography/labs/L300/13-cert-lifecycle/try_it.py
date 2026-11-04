"""Try it: two experiments on the certificate lifecycle (run: python try_it.py)."""
import datetime as dt
import random

import cert_lifecycle as cl
import solution_renewal as sol

ca_key, ca = cl.local_ca.make_root()
cert = cl.issue(ca_key, ca, cl.T0)

# 1) 100 servers renew the same 160 h certificate: without jitter vs with jitter.
start = cert.not_valid_before_utc  # count hours from notBefore so the result does not depend on today's date
fixed = {round(160 * 2 / 3)}
jittered = {round((sol.next_renewal(cert, random.Random(s)) - start) / cl.HOUR) for s in range(100)}
print(f"1) distinct renewal hours for 100 servers: no jitter {len(fixed)}, jitter {len(jittered)}")

# 2) How much client clock skew does a 1 h backdate absorb? Try 5 min, 59 min and 61 min slow.
for minutes in (5, 59, 61):
    ok = cl.handshake_ok(cert, ca, cl.T0 - dt.timedelta(minutes=minutes))
    print(f"2) client clock {minutes:>2} min slow: handshake {'ok' if ok else 'FAIL (not yet valid)'}")
