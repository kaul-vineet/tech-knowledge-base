# Lab 19-radio-auth — Securing constrained devices: authenticated radio frames

**Design question:** micro:bit MicroPython documents no hashlib/hmac/cryptolib module. How do we stop forged and
replayed radio frames anyway? Validation: **validated-stub** (SipHash checked against the reference vectors; the
board's speed is not measured). Decision: `adr/0019-siphash-mac-and-replay-window-at-the-gateway.md`.

| File | Purpose |
|---|---|
| `frame_auth.py` | Device + gateway, pure functions: `siphash24` (SipHash-2-4), `toy_tag` (CRC-16 over key + message, **NOT cryptographically secure**), `seal()`, `Counter` (counter blocks persisted in flash) |
| `verifier.py` | BEFORE (gateway): parse + CRC only — detects noise, not attackers |
| `solution.py` | AFTER (build task): known device -> SipHash MAC (`hmac.compare_digest`) -> 64-counter replay window; only authenticated frames move the window; JSON reject log |
| `attacks.py` | Seeded scenario on the stub radio (`radio.Air` loss 10 %, dup 5 %, reorder 10 %, corrupt 2 %): 3 boards x 60 frames; Eve replays 20, forges 20 (CRC recompute / toy state recovery / random tag) |
| `cost.py` | Per-frame cost: SipRounds, 64-bit ops, bytes on air, counter flash writes (CPython timing is informational only) |

## Step 1 — the options under attack
```bash
cd labs/L400/19-radio-auth
python3 attacks.py             # Windows: py attacks.py
```
Observed:
```
{"verifier": "verifier.py", "mode": "crc", "genuine_sent": 180, "genuine_intact": 158, "genuine_accepted": 158, "forged_accepted": 20, "replays_accepted": 18, "toy_state_recovered": false, "rejected": 7}
{"verifier": "solution.py", "mode": "toy", "genuine_sent": 180, "genuine_intact": 158, "genuine_accepted": 140, "forged_accepted": 19, "replays_accepted": 0, "toy_state_recovered": true, "rejected": 50}
{"verifier": "solution.py", "mode": "siphash", "genuine_sent": 180, "genuine_intact": 160, "genuine_accepted": 160, "forged_accepted": 0, "replays_accepted": 0, "toy_state_recovered": false, "rejected": 50}
```
`toy_state_recovered: true` = from 2 recorded frames, Eve found the 16-bit CRC state by trying all 65,536 values,
then tagged her forgeries. With the toy tag her fresh counters also pushed the window ahead: 18 genuine frames
were then rejected (140 of 158) — forgery became denial of service.

## Step 2 — cost
```bash
python3 cost.py
```
Observed (CPython microseconds vary by machine and load; they are NOT micro:bit numbers):
```
{"mode": "crc", "tag_bytes_on_air": 5, "cpython_us_per_tag": 279.0}
{"mode": "toy", "tag_bytes_on_air": 5, "cpython_us_per_tag": 499.2}
{"mode": "siphash", "tag_bytes_on_air": 17, "cpython_us_per_tag": 406.9, "rounds": 10, "ops64": 140}
{"counter_flash_writes_per_1000_frames": 10}
```

## Step 3 — failureLab symptom
```
test_forgeries_and_replays_get_in (test_fault.Symptom.test_forgeries_and_replays_get_in) ... ok
Ran 1 test in <time>
OK
```

## Step 4 — build task
```bash
BUILD_TARGET=mine python3 -m unittest -v test_build_task      # verifier.py: must FAIL
python3 -m unittest -v test_build_task                          # solution.py
```
Observed with `verifier.py`:
```
test_attack_scenario (test_build_task.Gateway.test_attack_scenario) ... FAIL
test_forged_frame_does_not_move_the_window (test_build_task.Gateway.test_forged_frame_does_not_move_the_window) ... FAIL
test_reordering_inside_the_window_is_fine_replays_are_not (test_build_task.Gateway.test_reordering_inside_the_window_is_fine_replays_are_not) ... FAIL
test_unknown_device_and_wrong_key_rejected (test_build_task.Gateway.test_unknown_device_and_wrong_key_rejected) ... ok
AssertionError: 0 != 160
AssertionError: None is not true
AssertionError: Lists differ: [False, False, False, False] != [True, True, True, True]
Ran 4 tests in <time>
FAILED (failures=3)
```
Observed with `solution.py`:
```
test_attack_scenario (test_build_task.Gateway.test_attack_scenario) ... ok
test_forged_frame_does_not_move_the_window (test_build_task.Gateway.test_forged_frame_does_not_move_the_window) ... ok
test_reordering_inside_the_window_is_fine_replays_are_not (test_build_task.Gateway.test_reordering_inside_the_window_is_fine_replays_are_not) ... ok
test_unknown_device_and_wrong_key_rejected (test_build_task.Gateway.test_unknown_device_and_wrong_key_rejected) ... ok
Ran 4 tests in <time>
OK
```

## Step 5 — fitness function (5 seeds: 0 forged, 0 replays, every intact genuine frame accepted)
```
test_no_forgery_no_replay_no_genuine_loss (test_fitness.Fitness.test_no_forgery_no_replay_no_genuine_loss) ... ok
Ran 1 test in <time>
OK
```

## Try it
```
try 1: genuine accepted 159 of 160 intact, forged accepted 0, replays accepted 0
try 2: genuine accepted 143 of 160 intact, forged accepted 0, replays accepted 0
```

## All tests
```
test_attack_scenario (test_build_task.Gateway.test_attack_scenario) ... ok
test_forged_frame_does_not_move_the_window (test_build_task.Gateway.test_forged_frame_does_not_move_the_window) ... ok
test_reordering_inside_the_window_is_fine_replays_are_not (test_build_task.Gateway.test_reordering_inside_the_window_is_fine_replays_are_not) ... ok
test_unknown_device_and_wrong_key_rejected (test_build_task.Gateway.test_unknown_device_and_wrong_key_rejected) ... ok
test_forgeries_and_replays_get_in (test_fault.Symptom.test_forgeries_and_replays_get_in) ... ok
test_no_forgery_no_replay_no_genuine_loss (test_fitness.Fitness.test_no_forgery_no_replay_no_genuine_loss) ... ok
test_reset_skips_ahead_and_flash_writes_are_rare (test_main.CounterReservation.test_reset_skips_ahead_and_flash_writes_are_rare) ... ok
test_crc_frame_passes_the_before_verifier (test_main.Mac.test_crc_frame_passes_the_before_verifier) ... ok
test_siphash_reference_vectors (test_main.Mac.test_siphash_reference_vectors) ... ok
test_toy_tag_is_a_crc_with_a_16_bit_secret_state (test_main.Mac.test_toy_tag_is_a_crc_with_a_16_bit_secret_state) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok
Ran 12 tests in <time>
OK
```

## In the simulator / on a board (pending-ci)
Paste `frame_auth.py` into the Python Editor and run `siphash24(bytes(range(16)), bytes(range(15)))`: it must print
the reference value 0xa129ca6149be45e5; `harness/simulator-l400.spec.js` also records `running_time()` for 100 tags.
Keys: generate with `secrets.token_bytes(16)` on the PC, copy to the board's file system over USB once; never in code,
never in a prompt.
