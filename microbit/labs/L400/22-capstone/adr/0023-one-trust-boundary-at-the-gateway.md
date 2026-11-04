# ADR 0023: One trust boundary at the gateway; the relay stays dumb

## Status
Accepted (2026-10-28).

## Context
In the capstone, frames cross the radio (anyone can send), the relay board (no keys) and USB serial
into the PC. Lab 19 showed that anything accepting unauthenticated state changes can be pushed around:
forged counters moved a replay window and cost genuine frames. Lab 17's relay drops a frame whose
sequence number is not newer than the last one it forwarded, so a forged frame with the next sequence
number would make the relay drop the genuine one. Keys on the relay would put them on one more board
that anyone can unplug.

## Decision
We will verify only at the gateway (device key, SipHash-2-4, 64-counter window) and keep the relay
keyless. The relay deduplicates on (seq, payload), so a frame it cannot authenticate never displaces
a different genuine frame. Everything behind the verifier (broker, store, twin, alarms, model) trusts
only verified readings. Measured on seed 22: Eve replayed 10 and forged 10 frames; 0 were stored; 9
were rejected on the MAC and 8 as replays (the rest were lost on the air); 3,599 of 3,600 genuine
readings were stored.

## Consequences
The relay forwards some garbage to the gateway (cheap). The gateway is the component to protect:
its key table, its broker credentials (Mosquitto with a password or TLS in CI/production), and its host.
