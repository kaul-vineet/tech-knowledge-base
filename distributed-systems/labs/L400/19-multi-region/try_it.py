"""tryIt experiments for lesson 19 (python try_it.py). Prints what actually happens."""
import solution_multiregion as mr
from helpers import base

# tryIt 1: follower reads with the chosen design (majority-sync, leader eu): local read vs read at the leader
calm = mr.simulate(mr.DESIGN)
for region in ("us", "ap"):
    print(f"tryIt 1: {region} follower read: ~{2 * base(region, region):.0f} ms, stale by up to"
          f" {calm['lag_p99_at'][region]} ms (p99 lag); leader read: ~{2 * base(region, 'eu'):.0f} ms + jitter, current"
          f" if the leader confirms it still leads (Raft section 8)")

# tryIt 2: a LAN-style election timeout (150-300 ms instead of 1-2 s) on the same WAN
for timeout in ((1000.0, 2000.0), (150.0, 300.0)):
    mr.ELECTION_MS = timeout
    m = mr.evaluate(mr.DESIGN)
    print(f"tryIt 2: election timeout {timeout[0]:.0f}-{timeout[1]:.0f} ms -> RTO {m['rto_ms']} ms,"
          f" {m['rejected']} writes rejected during failover, RPO {m['rpo_writes']}")
