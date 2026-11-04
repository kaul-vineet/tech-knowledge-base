# ADR 0002: Delta frames on the radio, a delta-state CRDT and push-pull gossip behind it

## Status
Accepted (L600 #04). Guarded by `tests/test_seams.py` S1/S5, `tests/test_milestones.py` M2/M3, scorecard F2.

## Context
The micro:bit radio sends messages of `length` bytes (default 32, at most 251; the sender truncates a longer
message). A state-based CRDT ships its whole state on every sync: one device's 12-hour log alone is
720 x 9 B = 6,480 B = 224 frames of 29 B payload. Loss is 30 % per delivery and both gateways may hear a frame.
Gateways and backend replicas are partitioned for hours (g2 4-8 h, g1 down 1 h).

## Decision
1. Device -> gateway: only unacked records, oldest first, 3 per 32-byte frame (3 B header + 3 x 9 B).
   A gateway acks (boot, contiguous high-water mark) per boot, from its durable store; the device deletes only
   records at or below an acked mark. A frame that is not a whole number of records is rejected, never half-parsed.
2. Replicas hold a grow-only map dot -> reading with a compact causal context: a version vector of contiguous
   marks (the L400 #18 G-Counter shape, merge = per-slot max) plus a dot cloud (Almeida et al., delta-state CRDTs).
3. Every 5 minutes each live node picks one reachable peer at random and swaps deltas both ways (push-pull
   anti-entropy, Demers et al.).

## Consequences
+ Frames stay at 30 B; the merge is a join (300/300 law checks), so loss, duplicates and reordering only delay.
+ 5 replicas agreed within 3 rounds in 200 seeded experiments (threshold 4).
- The digest grows with (device x boot) entries and with gaps in the cloud; with thousands of devices send
  digests per shard or use Merkle trees.
- Acks are per frame; under 30 % loss the device retries (2,835 attempts for 1,440 syncs in the seeded run;
  the same run with cumulative-only acks (`selective_ack=False`) needs 13,177 frames instead of 9,752 - see
  try it 2 for the case where selective acks are essential).
