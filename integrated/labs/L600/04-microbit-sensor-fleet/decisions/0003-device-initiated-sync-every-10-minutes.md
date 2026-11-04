# ADR 0003: Devices start the sync, every 10 samples, with the radio off in between

## Status
Accepted (L600 #04). Guarded by scorecard S3/F3 and `tests/test_fitness.py` F3.

## Context
Between samples the board should be in Deep Sleep; a sleeping board cannot listen, so a gateway cannot push or
poll. The microbit L300 #14 model gives the board 30 mA while awake (worst-case budget), a conservative 0.5 mA
Deep Sleep floor (an assumption, not a measurement), 20 ms awake per wake-up and 1,250 mAh for 2 x AAA.
Each sync attempt keeps the radio on for an ack window; ACK_WAIT_MS = 50 is our ASSUMPTION (no airtime model).
Target: >= 2,000 h per device (about a school term).

## Decision
The device syncs after every SYNC_EVERY = 10 samples (10 min), staggered by device id, at most 3 attempts of up
to 8 frames, and turns the radio off afterwards.

## Consequences
+ Model: 2,419.7 h for the worst device in the seeded run (target 2,000 h).
- Freshness: a reading reaches a gateway up to ~10 min later in normal operation; p95 was 4,020 s in the
  seeded run because of the 3-hour radio partition. Alarms must not depend on this path.
- Sync every sample: 2,212.4 h, still above target in the model (try it 1); a 10 s sync with 3 attempts each
  (360 x 170 ms awake per hour) falls to 1,236.0 h.
  The 0.5 mA floor dominates: measure it on a real board before trusting any of these hours.
