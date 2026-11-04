## Why it matters
Users sit in three regions. Writes that wait for another continent feel slow; writes that do not wait can vanish when a region goes dark. "Multi-region" is not a feature you switch on: it is a set of choices about where the leader lives, how many regions must hold a write before you acknowledge it, and what happens in the seconds after a region fails. Those choices decide two numbers the business cares about: how much acknowledged data can be lost (**RPO**, recovery point objective) and how long writes are unavailable (**RTO**, recovery time objective), both terms from contingency planning (NIST SP 800-34).

## Mental model
A write's latency is the sum of the network legs it must wait for:

```
async, leader L:          client -> L -> client                    (followers catch up later)
majority-sync, leader L:  client -> L -> nearest follower -> L -> client
multi-leader:             client -> local leader -> client        (others catch up later)
leaderless W=2:           client region -> all regions, wait for the 2nd fastest reply
```

Everything acknowledged before it reached a second region is exposed when the first region fails. Everything that waits for a second region pays that round trip on every write.

## Design space
- **Single leader, async**: fastest writes for the leader's region; RPO > 0 (the replication lag window is lost).
- **Single leader, majority-sync** (Raft-style): commit after the first follower acknowledges; RPO 0, because the new leader is chosen from the most up-to-date survivors; RTO = one election.
- **Multi-leader**: every region writes locally; concurrent writes to the same key conflict and need merge rules (lesson 18).
- **Leaderless quorums**: no failover at all; conflicts and read repair instead (lesson 17).
- **Leader placement**: the leader's region, and how close it is to its nearest follower, sets everyone's commit cost.
- **Follower reads**: local and fast, but stale by the replication lag; reading at the leader is current only if it confirms it still leads (Raft section 8).

## How to decide
1. Write the brief as numbers: p99 write budget per user region, RPO, RTO, "no conflicting writes" yes/no.
2. Simulate each design with realistic latencies and a slow tail, fail a whole region, and measure p99, lost acknowledged writes and time to the first successful write.
3. Choose leader placement by measurement (traffic-weighted p99), not by history.

Worked example (lab output, seed 19; one-way latencies us-eu 40, eu-ap 70, us-ap 110 ms are assumptions; 50/35/15% traffic; region failure at 10 s): the deployed design, async with the leader in ap, loses **16 acknowledged writes** when ap fails. Async with the leader in us loses 17. Majority-sync loses none at any placement, with an RTO of 1,009-1,313 ms (a 1-2 s election timeout plus a vote). Multi-leader and leaderless keep writing through the failure (first successful write 65 ms after it) but accept 434 and 409 conflicting concurrent writes. Placement: majority-sync with the leader in us gives eu users p99 354.9 ms, over the 350 ms budget; with the leader in eu, us/eu/ap p99 is 304.6/267.8/341.7 ms. `place_leader` picks eu: it is the middle region, so its nearest follower is close for everyone. Follower reads in ap are local (about 2 ms) but up to 103.6 ms stale at p99.

## Failure modes at scale
- **Head-of-line blocking**: one slow message on an ordered replication stream delays every entry behind it; this is why majority-sync p99 sits far above the base round trip.
- **Thin margins**: over 20 seeds the us p99 peaked at 339.2 ms against a 350 ms budget; a traffic shift towards ap or a heavier tail breaks it. A fitness test catches the drift.
- **Election timeout tuning**: a LAN-style 150-300 ms timeout cut RTO to 278 ms in the simulation, but over a real WAN it triggers needless elections whenever latency spikes (not modelled).
- **Split-brain writes** in multi-leader designs surface later as lost updates or oversold stock.

## Common mistakes
- Quoting RPO 0 for asynchronous replication because "the lag is usually small".
- Placing the leader where most users are, without measuring commit paths.
- Counting a region failure as "covered" without measuring the election and client redirect time.
