# Concept: the classroom environmental monitor network (capstone)

## Overview
Six micro:bits measure temperature, light and motion around a classroom. A seventh board, the relay,
sits on the PC's USB port. The PC is the gateway: it verifies every frame, publishes MQTT, stores
readings, runs a digital twin, raises alarms and lets a local model explain them. Nothing new is
invented here. The capstone is built from the L100–L400 labs and proven by a seeded end-to-end run
that prints a scorecard. As in the LPC1768 guide's capstone, the deterministic core decides and the
AI only explains.

## Architecture walkthrough
1. **Firmware** (`build_firmware.py`). The board program is generated from lab 19's `frame_auth.py`
   and lab 17's `solution.py`, plus four small patches checked to match exactly once: SipHash tags,
   a 96-byte radio length, and relay dedupe on (seq, payload). There is no copy-paste; edit the labs.
   Each board also runs lab 21's firmware alarm locally.
2. **Radio** (lab 12 → 17). Stop-and-wait ARQ with a random phase and jittered timeouts. n5's link
   degrades from 300 s. Eve, a seventh radio, replays 10 recorded frames and forges 10 "45 C" frames.
3. **Gateway** (lab 15 → 19). The serial framer, then the trust boundary: known device, MAC, replay
   window. Only then come MQTT QoS 1 and an idempotent SQLite store keyed on (dev, seq).
4. **Fleet** (lab 18). A two-phase staged rollout: good v2, then bad v3 (wrong group), halted at the
   canary.
5. **Twin** (lab 20). Calibrated on the first 3 minutes of this run's own telemetry, then a CUSUM drift
   check per board and signal.
6. **Alarms and agent** (lab 21). Rules on the snapshot: TEMP_HIGH, drift, auth rejects. The model gets
   a frozen copy that includes n4's injected label, and its reply is checked.
7. **Dashboard.** A CSV for Apache Superset and a Prometheus text file for Grafana. Opening them in
   those tools is a manual step.

## What the run shows (seed 22, 600 s, `run_capstone.py`)
- 3,599 of 3,600 readings stored (one n5 reading was given up as its link failed), p95 324 ms.
- 0 forged or replayed readings stored; the gateway rejected 9 on MAC and 8 as replays.
- Fleet: 0 unacknowledged ticks, 1 device on the bad version, final versions 222222.
- n5's link drift was found at window 14 (drift from window 10). The sun on n4 also showed as
  DRIFT_TEMP, and n6 raised one DRIFT_LAT that the model, which treats links as independent, cannot explain.
- TEMP_HIGH at n4 was raised by both the gateway and the firmware. The model's reply obeyed the
  injected label, was rejected, and the record's digest was unchanged. The operator saw the code's note.
- The scorecard is 10/10 and also passes on seed 23, a seed the design was not tuned on.

## How it ties L100–L400 together
L100 taught sensors and the display. L200 added radio and logging. L300 hardened the radio (ARQ, CRC),
structure, power and the serial gateway. L400 made the decisions: architecture (17), fleet change (18),
trust boundary (19), model-based monitoring (20) and the place of AI (21). Each decision has an ADR and
a fitness test, and the capstone runs them together. The pending items are honest: the simulator, real
boards, Mosquitto, a real local model, and MicroPython timing.
