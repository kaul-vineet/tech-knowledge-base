# ADR 0017: Radio relay to one serial gateway, with desynchronised senders

## Status
Accepted (2026-10-28). Measured on the CPython stub only (validated-stub); revisit after the
simulator/board measurements listed in the lesson's `pendingCi`.

## Context
A classroom needs six micro:bit sensor boards (temperature, light, motion) spread around the room,
feeding one PC that publishes to an MQTT broker, stores readings and drives a dashboard. Constraints:
at least 99 % of readings stored, p95 sensor-to-store latency of 2 s or less, at most one USB cable to
the PC, MicroPython only (no Bluetooth API for user code on micro:bit V2: only BLE flashing is
implemented). The lab measured three options on the stub network (`options.py`, seed 17, per-link loss
5-15 %):

* Direct serial (a cable per board): 180/180 stored, p95 13 ms, but six cables run across a classroom.
* Radio relay as first written (`node.py`): 160/180 (88.9 %), p95 9,578 ms, 56 readings given up,
  149 frames dropped by the relay's 3-frame queue. Every board sampled at t = 0 and retried on the
  same 100/200/400 ms deadlines, so their frames arrived together and overflowed the queue.
* Radio relay with random sampling phase, jittered timeouts, a 12-frame queue and 64-byte frames (`solution.py`):
  180/180, p95 153 ms, 0 given up. With 24 boards: 480/480. With the queue alone (no jitter) 24 boards
  stored only 151/480 (31.5 %); with the jitter alone (queue 3) 480/480.
* BLE: not measurable here (see above); it would need a different firmware stack.

## Decision
We will use one relay micro:bit on the PC's USB port and radio from the sensor boards, with lab 12's
stop-and-wait ARQ, a random sampling phase per board, jittered retransmit timeouts, a 12-frame
receive queue and a 64-byte radio length (frames carry a growing counter and timestamp: at 32 bytes they
overflowed after about 1,000 s in lab 20's 20-minute run, and every reading after that was lost). The gateway reuses lab 15's framer, publishes MQTT QoS 1 and stores with an idempotent
(dev, seq) key. Fitness function `test_fitness.py` keeps it true: 5 seeds, delivery >= 99 %, p95 <= 2 s,
no reading given up.

## Consequences
* One cable, boards can move; desynchronisation (not a bigger queue) is what makes it scale in the model.
* The queue costs RAM: 12 buffers of 64 bytes, about 768 B per board (MicroPython's exact allocation unverified).
* The stub has no airtime, collision or CPU model: real limits (relay CPU per frame, radio collisions)
  are still unmeasured. The relay is a single point of failure; a second relay needs dedupe across relays.
* Radio frames are not authenticated: ADR 0019 adds that at the gateway, the trust boundary.
