# Lab 18-fleet-config — Device fleet management: versioned config over the radio

**Design question:** how do we change six boards' configuration over the radio so that no board ever runs a
version the gateway has not acknowledged, and a bad config cannot strand a board? Validation: **validated-stub**.
Decision: `adr/0018-two-phase-config-with-canary-rollout.md`.

| File | Purpose |
|---|---|
| `config_agent.py` | BEFORE (device, MicroPython): one-phase — apply on receipt, then ack |
| `solution.py` | AFTER (build task, device): prepare/stage (K), commit (G) -> apply, report A every 500 ms, probation 3 s, rollback (R) |
| `fleet.py` | Gateway (PC): registry of acknowledged versions per device; rollout waves (push-all or canary 1 -> 2 -> 3), halt on R/N/timeout; JSON event log |
| `fleet_sim.py` | Six stub boards + gateway radio on `LinkAir` (10 % loss): v2 (good) at 0 s, v3 (radio group 99) at 15 s; counts the fitness invariant every tick |
| tests + `try_it.*` | basics, failureLab, build task, fitness, tryIt |

## Step 1 — the options on the same scenario
```bash
cd labs/L400/18-fleet-config
python3 fleet_sim.py           # Windows: py fleet_sim.py
```
Observed:
```
{"device": "config_agent.py", "strategy": "push-all", "unacked_ticks": 12086, "max_on_bad": 5, "deaf_device_ms": 120800, "jobs": "v2 done @310, v3 halted @23010", "final": "333332", "gw_sent": 177}
{"device": "solution.py", "strategy": "push-all", "unacked_ticks": 0, "max_on_bad": 4, "deaf_device_ms": 12000, "jobs": "v2 done @1210, v3 halted @18310", "final": "222222", "gw_sent": 99}
{"device": "solution.py", "strategy": "staged", "unacked_ticks": 0, "max_on_bad": 1, "deaf_device_ms": 3000, "jobs": "v2 done @1850, v3 halted @18610", "final": "222222", "gw_sent": 34}
```
`unacked_ticks` = device-ticks spent on a version the gateway never acknowledged (the fitness invariant);
`deaf_device_ms` = time devices spent on a radio group the gateway does not use; `final` = versions of n1..n6.

## Step 2 — failureLab symptom
```
test_unacknowledged_configs_and_bricked_devices (test_fault.Symptom.test_unacknowledged_configs_and_bricked_devices) ... ok
Ran 1 test in <time>
OK
```

## Step 3 — build task
```bash
BUILD_TARGET=mine python3 -m unittest -v test_build_task      # config_agent.py: must FAIL
python3 -m unittest -v test_build_task                          # solution.py
```
Observed with `config_agent.py`:
```
test_bad_config_rolls_back_everywhere (test_build_task.TwoPhase.test_bad_config_rolls_back_everywhere) ... FAIL
test_never_runs_an_unacknowledged_config (test_build_task.TwoPhase.test_never_runs_an_unacknowledged_config) ... FAIL
AssertionError: Lists differ: [3, 3, 3, 3, 3, 2] != [2, 2, 2, 2, 2, 2]
AssertionError: 12086 != 0 : push-all
Ran 2 tests in <time>
FAILED (failures=2)
```
Observed with `solution.py`:
```
test_bad_config_rolls_back_everywhere (test_build_task.TwoPhase.test_bad_config_rolls_back_everywhere) ... ok
test_never_runs_an_unacknowledged_config (test_build_task.TwoPhase.test_never_runs_an_unacknowledged_config) ... ok
Ran 2 tests in <time>
OK
```

## Step 4 — fitness function
5 seeds x 10 %/30 % loss x both strategies: `unacked_ticks == 0`; staged blast radius <= 1.
```
test_no_device_runs_an_unacknowledged_config (test_fitness.Fitness.test_no_device_runs_an_unacknowledged_config) ... ok
Ran 1 test in <time>
OK
```

## Try it
```
try 1: jobs: v2 halted @3310, v3 halted @18310 | final versions 111111 | unacked_ticks 0
try 2: jobs: v2 halted @8920, v3 halted @16810 | final versions 111111 | unacked_ticks 0
```
Both edits keep the invariant (0 unacked ticks) but turn packet loss into **false rollbacks**: the GOOD v2 is
rolled back (final 111111) and the rollout halts.

## All tests
```
test_bad_config_rolls_back_everywhere (test_build_task.TwoPhase.test_bad_config_rolls_back_everywhere) ... ok
test_never_runs_an_unacknowledged_config (test_build_task.TwoPhase.test_never_runs_an_unacknowledged_config) ... ok
test_unacknowledged_configs_and_bricked_devices (test_fault.Symptom.test_unacknowledged_configs_and_bricked_devices) ... ok
test_no_device_runs_an_unacknowledged_config (test_fitness.Fitness.test_no_device_runs_an_unacknowledged_config) ... ok
test_frames (test_main.Config.test_frames) ... ok
test_good_config_reaches_every_device_on_a_quiet_link (test_main.Config.test_good_config_reaches_every_device_on_a_quiet_link) ... ok
test_parse_and_validate (test_main.Config.test_parse_and_validate) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok
Ran 9 tests in <time>
OK
```

## Limits
Configuration lives in RAM (a reset returns to factory); on a board persist last-good with `open()`/`write()`
(~30 kB flash file system). Config frames are CRC-checked, not authenticated (lab 19). Simulator run pending-ci.
