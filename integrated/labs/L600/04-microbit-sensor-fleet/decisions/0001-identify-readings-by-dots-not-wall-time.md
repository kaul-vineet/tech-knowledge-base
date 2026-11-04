# ADR 0001: Identify readings by dots (device, boot, seq), not by device wall time

## Status
Accepted (L600 #04). Guarded by `tests/test_failure_lab.py` and scorecard lines S2 and F1.

## Context
A micro:bit has no real-time clock: `running_time()` counts milliseconds since the board was switched on or
restarted (MicroPython docs). Our devices build a wall time from the epoch in the last gateway ack plus
`running_time()`, so it steps backwards after a reboot (d07 at minute 300) and every time a device hears gateway
g2, whose clock is 300 s slow. The obvious backend - one row per (device, timestamp), last write wins, as a
time-series store does with a duplicate key - silently overwrote 1,421 of 14,400 readings in the seeded run
(`--inject wallclock-lww`), while every gateway had acknowledged them and all replicas agreed.

Options considered: (a) LWW by wall time - loses data whenever time repeats; (b) a hybrid logical clock on the
devices - monotonic, but needs state that survives a reboot and every incoming timestamp, and a timestamp is
still not an identity; (c) a per-device counter plus a boot number persisted in flash (one flash write per boot).

## Decision
Every reading is identified by its dot (dev, boot, seq). seq restarts at 1 on each boot; boot is stored in flash.
Per-device order is (boot, seq). Wall time travels as a display attribute (`deviceTime`) and is never a key.

## Consequences
+ Zero readings lost under reboots and clock steps (F1 on seeds 4, 5, 6).
+ Duplicates from radio retries, two gateways and gossip are idempotent: the dot is the idempotency key.
- Cross-device order is not causal: "which board was hotter first" needs a HLC or gateway receive time.
- /v1 shows only `seq`, which goes backwards after a reboot; /v2 adds `boot` (ADR 0004).
- If flash is erased, boot restarts at 1 and dots repeat: re-provision with a new device id.
