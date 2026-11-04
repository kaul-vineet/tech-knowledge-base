# Lab 17-edge-to-cloud — Edge-to-cloud architecture: sensors to dashboard

**Design question:** how should six classroom boards reach the broker, storage and dashboard, with
>= 99 % of readings stored, p95 <= 2 s and at most one cable to the PC? Validation: **validated-stub**
(CPython stub boards, simulated time; no radio airtime/collision model). Decision: `adr/0017-radio-relay-to-one-serial-gateway.md`.

| File | Purpose |
|---|---|
| `node.py` | BEFORE: sensor + relay on one file (lab 12 ARQ per sensor, lab 15 serial frames); all boards in lock-step, radio defaults |
| `solution.py` | AFTER (build task): random sampling phase, jittered timeouts, queue 12, 64-byte frames |
| `edge_sim.py` | Runs N stub boards + relay over `LinkAir` (seeded per-link loss) -> lab 15 framer (reused) -> MiniBroker (MQTT-style QoS 1) -> SQLite -> summary |
| `options.py` | The three options measured on the same network: direct serial, radio relay (before/after), BLE (not measurable) |
| `test_main.py`, `test_fault.py`, `test_build_task.py`, `test_fitness.py`, `try_it.*` | Basics, failureLab symptom, build-task proof, fitness function, tryIt |
| `../_edge/` | Shared L400 helpers: `simnet.py` (LinkAir, percentile, reuse), `minibroker.py`, `store.py` (SQLite, CSV, Prometheus text) |

## Run in the simulator (pending-ci)
Flash `solution.py` on two Python Editor tabs (or `harness/host.html?boards=2`), call `main("relay", "relay")`
on one and `main("sensor", "n1")` on the other: the relay's serial shows `$0NN n1,1,...*CRC` frames.
`harness/simulator-l400.spec.js` automates it — **pending-ci, not yet observed**.

## Step 1 — measure the options (stub, no board)
```bash
cd labs/L400/17-edge-to-cloud
python3 options.py            # Windows (PowerShell): py options.py
```
Observed (Python 3.12.15, Linux sandbox):
```
{"file": "solution.py", "sensors": 6, "sampled": 180, "stored": 180, "delivery_pct": 100.0, "p50_ms": 13, "p95_ms": 13, "max_ms": 13, "tx": 0, "retx": 0, "gave_up": 0, "relay_queue_drops": 0, "sensor_queue_drops": 0, "bad_serial": 0, "option": "A direct serial", "usb_cables": 6}
{"file": "node.py", "sensors": 6, "sampled": 180, "stored": 160, "delivery_pct": 88.9, "p50_ms": 2128, "p95_ms": 9578, "max_ms": 10568, "tx": 549, "retx": 369, "gave_up": 56, "relay_queue_drops": 149, "sensor_queue_drops": 1027, "bad_serial": 0, "option": "B radio relay (node.py)", "usb_cables": 1}
{"file": "solution.py", "sensors": 6, "sampled": 180, "stored": 180, "delivery_pct": 100.0, "p50_ms": 13, "p95_ms": 153, "max_ms": 393, "tx": 210, "retx": 30, "gave_up": 0, "relay_queue_drops": 0, "sensor_queue_drops": 0, "bad_serial": 0, "option": "B radio relay (solution.py)", "usb_cables": 1}
{"option": "C BLE", "measured": false, "why": "micro:bit MicroPython V2: only BLE flashing is implemented; no BLE API for user code"}
```

## Step 2 — the failureLab symptom
```bash
python3 -m unittest -v test_fault
```
```
test_six_boards_overflow_the_relay (test_fault.Symptom.test_six_boards_overflow_the_relay) ... ok
Ran 1 test in <time>
OK
```

## Step 3 — build task: fails before, passes after
```bash
BUILD_TARGET=mine python3 -m unittest -v test_build_task      # macOS: your file = node.py
$env:BUILD_TARGET="mine"; py -m unittest -v test_build_task   # Windows PowerShell
python3 -m unittest -v test_build_task                          # solution.py
```
Observed with `node.py`:
```
test_24_boards_still_deliver (test_build_task.Classroom.test_24_boards_still_deliver) ... FAIL
test_frames_still_fit_after_a_school_day (test_build_task.Classroom.test_frames_still_fit_after_a_school_day) ... FAIL
test_six_boards_deliver_everything_fast (test_build_task.Classroom.test_six_boards_deliver_everything_fast) ... FAIL
AssertionError: 8.8 not greater than or equal to 99.0
AssertionError: 38 not less than or equal to 32
AssertionError: 88.9 not greater than or equal to 99.0
Ran 3 tests in <time>
FAILED (failures=3)
```
Observed with `solution.py`:
```
test_24_boards_still_deliver (test_build_task.Classroom.test_24_boards_still_deliver) ... ok
test_frames_still_fit_after_a_school_day (test_build_task.Classroom.test_frames_still_fit_after_a_school_day) ... ok
test_six_boards_deliver_everything_fast (test_build_task.Classroom.test_six_boards_deliver_everything_fast) ... ok
Ran 3 tests in <time>
OK
```

## Step 4 — fitness function (keeps ADR 0017 true)
```bash
python3 -m unittest -v test_fitness
```
```
test_delivery_and_latency_across_seeds (test_fitness.Fitness.test_delivery_and_latency_across_seeds) ... ok
Ran 1 test in <time>
OK
```

## Try it
```bash
python3 try_it.py
```
```
try 1: delivered 480/480 (100.0%), p95 165 ms, gave_up 0, relay drops 0, sensor drops 176
try 2: delivered 151/480 (31.5%), p95 19031 ms, gave_up 216, relay drops 570, sensor drops 15787
```
Try 1 keeps the jitter and goes back to the default 3-frame queue; try 2 keeps the 12-frame queue and removes
the jitter. With 24 boards, desynchronisation — not the buffer — is what holds delivery at 100 %.

## All tests in this lab
```
test_24_boards_still_deliver (test_build_task.Classroom.test_24_boards_still_deliver) ... ok
test_frames_still_fit_after_a_school_day (test_build_task.Classroom.test_frames_still_fit_after_a_school_day) ... ok
test_six_boards_deliver_everything_fast (test_build_task.Classroom.test_six_boards_deliver_everything_fast) ... ok
test_six_boards_overflow_the_relay (test_fault.Symptom.test_six_boards_overflow_the_relay) ... ok
test_delivery_and_latency_across_seeds (test_fitness.Fitness.test_delivery_and_latency_across_seeds) ... ok
test_relay_acks_dedupes_and_frames_for_the_gateway (test_main.Frames.test_relay_acks_dedupes_and_frames_for_the_gateway) ... ok
test_round_trip_and_crc (test_main.Frames.test_round_trip_and_crc) ... ok
test_single_sensor_is_fine (test_main.OneSensor.test_single_sensor_is_fine) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok
Ran 10 tests in <time>
OK
```
Run time is dominated by loading seven stub boards per run (about 1 minute on the sandbox). macOS and Windows: CI matrix — pending-ci.

## Limits of this lab
The stub radio has no airtime, collisions or range, and stub boards cost no CPU: latency here is protocol latency
(timeouts, queues) plus UART time at 115,200 baud. BLE cannot be measured (MicroPython V2 implements only BLE flashing).
