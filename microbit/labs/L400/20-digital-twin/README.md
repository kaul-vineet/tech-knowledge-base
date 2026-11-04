# Lab 20-digital-twin — Digital twin of the sensor network

**Design question:** how does a model of the network, fed by gateway telemetry, notice slow drift within 5 minutes
without alarming on noise? Validation: **validated-stub** (telemetry recorded from lab 17's stub network).
Decision: `adr/0020-cusum-drift-check-on-a-calibrated-twin.md`.

| File | Purpose |
|---|---|
| `twin_model.py` | The twin: Monte Carlo of lab 17's ARQ (retry share, p95 latency for a loss l), first-order room model, calibration on the first 6 windows |
| `twin.py` | BEFORE: memoryless check, alarm when \|z\| > 2 in one window |
| `solution.py` | AFTER (build task): tabular CUSUM per device and signal, K = 0.75, H = 5, latched alarm, JSON log |
| `make_telemetry.py` | Regenerates `telemetry/classroom_seed20.csv` from lab 17's network: 1,200 s, n5's link loss 0.15 -> 0.45 and n3 +1.5 C from 600 s (about 1 minute) |
| `drift_eval.py` | Feeds the fixture to a twin, scores detection delay and false alarms; 1,000 synthetic nominal windows from the twin's own model |

## Step 1 — compare the detectors
```bash
cd labs/L400/20-digital-twin
python3 drift_eval.py          # Windows: py drift_eval.py
```
Observed:
```
{"detected_after_windows": {"n3 DRIFT_TEMP": 7, "n5 DRIFT_LAT": 7}, "false_alarms_fixture": 13, "false_alarms_per_1000_synthetic": 80, "twin": "twin.py"}
{"detected_after_windows": {"n3 DRIFT_TEMP": 8, "n5 DRIFT_LAT": 9}, "false_alarms_fixture": 2, "false_alarms_per_1000_synthetic": 0, "twin": "solution.py"}
```
Detection is counted in 30-reading windows after the drift started (window 20). The 2 alarms CUSUM raises on nominal
streams of the run are n2 at 450 s (two windows with 5 of 30 readings retried) and n1 at 1,050 s, when n5's retries
were loading the shared relay — a coupling the twin does not model.

## Step 2 — failureLab symptom
```
test_cries_wolf (test_fault.Symptom.test_cries_wolf) ... ok
Ran 1 test in <time>
OK
```

## Step 3 — build task
```bash
BUILD_TARGET=mine python3 -m unittest -v test_build_task      # twin.py: must FAIL
python3 -m unittest -v test_build_task                          # solution.py
```
Observed with `twin.py`:
```
test_finds_both_drifts_within_ten_windows (test_build_task.DriftCheck.test_finds_both_drifts_within_ten_windows) ... ok
test_rarely_cries_wolf (test_build_task.DriftCheck.test_rarely_cries_wolf) ... FAIL
AssertionError: 13 not less than or equal to 2
Ran 2 tests in <time>
FAILED (failures=1)
```
Observed with `solution.py`:
```
test_finds_both_drifts_within_ten_windows (test_build_task.DriftCheck.test_finds_both_drifts_within_ten_windows) ... ok
test_rarely_cries_wolf (test_build_task.DriftCheck.test_rarely_cries_wolf) ... ok
Ran 2 tests in <time>
OK
```

## Step 4 — fitness function
```
test_detection_delay (test_fitness.Fitness.test_detection_delay) ... ok
test_false_alarm_rate (test_fitness.Fitness.test_false_alarm_rate) ... ok
Ran 2 tests in <time>
OK
```

## Try it
```
try 1: {"n3 DRIFT_TEMP": 10, "n5 DRIFT_LAT": 9} | false alarms: fixture 3, synthetic 12 per 1000
try 2: {"n3 DRIFT_TEMP": 5} | false alarms: fixture 6, synthetic 74 per 1000
```
Try 2 (K = 0): n5's sum crossed H before the drift began, the alarm latched early (counted as false) and the real
drift was never reported.

## All tests
```
test_finds_both_drifts_within_ten_windows (test_build_task.DriftCheck.test_finds_both_drifts_within_ten_windows) ... ok
test_rarely_cries_wolf (test_build_task.DriftCheck.test_rarely_cries_wolf) ... ok
test_cries_wolf (test_fault.Symptom.test_cries_wolf) ... ok
test_detection_delay (test_fitness.Fitness.test_detection_delay) ... ok
test_false_alarm_rate (test_fitness.Fitness.test_false_alarm_rate) ... ok
test_first_150_s_regenerate_identically (test_main.Fixture.test_first_150_s_regenerate_identically) ... ok
test_calibration_finds_each_links_loss (test_main.Model.test_calibration_finds_each_links_loss) ... ok
test_retry_share_is_about_the_loss (test_main.Model.test_retry_share_is_about_the_loss) ... ok
test_timer_constants_match_lab_17 (test_main.Model.test_timer_constants_match_lab_17) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok
Ran 11 tests in <time>
OK
```
`test_main.Fixture` regenerates the first 150 s of the telemetry and checks it equals the saved file (provenance).
