# Lab 13-nonblocking-scheduler — Non-blocking firmware structure

| File | Purpose |
|---|---|
| `main.py` | BEFORE: tap counter + temperature, `sleep(1000)` in the loop (works for slow, deliberate presses) |
| `solution.py` | AFTER (build task): cooperative scheduler on `running_time()`, no sleep in the loop, task periods and budgets, overrun/late JSON lines, error containment and a safe state |
| `tap_sim.py` | Seeded quick taps on the stub's timeline (`microbit._at`); runs either design |
| `test_main.py` | Happy path of `main.py`: a 1.5 s press counts, a long press clears, one JSON line per second |
| `test_fault.py` | The failureLab symptom: 8 quick taps, 1 counted |
| `test_build_task.py` | Proof: fails on `main.py`, passes on `solution.py` |
| `try_it.py`, `try_it.json`, `test_try_it.py` | The two `tryIt` items (edits to `solution.py`) |

## Run in the simulator
Paste `main.py`, open serial: press and **hold** A for about 1.5 s → `tap 1`. Click A quickly three
times → usually nothing. Then paste `solution.py` and click quickly three times → `tap 1`, `tap 2`,
`tap 3`. Checked by `harness/simulator-l300.spec.js` — **pending-ci, not yet observed**.

## Steps 1-2 — happy path and failureLab (stub)
```bash
cd labs/L300/13-nonblocking-scheduler
python3 tap_sim.py           # Windows (PowerShell): py tap_sim.py
```
Observed (Python 3.12.15, Linux sandbox):
```
taps at (ms): [932, 1680, 2630, 3695, 4645, 5655, 6689, 7744]
main.py     (sleep 1000): counted 1 of 8
solution.py (scheduler) : counted 8 of 8; stats {'runs': 610, 'overruns': 0, 'missed': 0, 'errors': 0}
```
```bash
python3 -m unittest -v test_main test_fault
```
```
test_deliberate_press_counts (test_main.HappyPath.test_deliberate_press_counts) ... ok
test_long_press_clears (test_main.HappyPath.test_long_press_clears) ... ok
test_sensor_line_is_json_once_per_second (test_main.HappyPath.test_sensor_line_is_json_once_per_second) ... ok
test_quick_taps_are_missed (test_fault.Symptom.test_quick_taps_are_missed) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.006s

OK
```

## Steps 3-5 — build task: fails before, passes after
```bash
BUILD_FILE=main.py python3 -m unittest -v test_build_task          # macOS (zsh): BEFORE
$env:BUILD_FILE="main.py"; py -m unittest -v test_build_task      # Windows (PowerShell)
python3 -m unittest -v test_build_task                              # AFTER: solution.py
```
Observed with `main.py` (summary lines):
```
test_every_quick_tap_counts (test_build_task.Scheduler.test_every_quick_tap_counts) ... FAIL
test_failing_task_leads_to_safe_state (test_build_task.Scheduler.test_failing_task_leads_to_safe_state) ... ERROR
test_long_press_still_clears (test_build_task.Scheduler.test_long_press_still_clears) ... ERROR
test_no_overruns_on_the_happy_path (test_build_task.Scheduler.test_no_overruns_on_the_happy_path) ... ERROR
test_overrun_is_logged (test_build_task.Scheduler.test_overrun_is_logged) ... ERROR
test_sensor_keeps_its_period (test_build_task.Scheduler.test_sensor_keeps_its_period) ... ERROR
ERROR: test_failing_task_leads_to_safe_state (test_build_task.Scheduler.test_failing_task_leads_to_safe_state)
AttributeError: module 'lab_13_nonblocking_scheduler' has no attribute 'new_scheduler'
ERROR: test_long_press_still_clears (test_build_task.Scheduler.test_long_press_still_clears)
AttributeError: module 'lab_13_nonblocking_scheduler' has no attribute 'new_scheduler'
ERROR: test_no_overruns_on_the_happy_path (test_build_task.Scheduler.test_no_overruns_on_the_happy_path)
AttributeError: module 'lab_13_nonblocking_scheduler' has no attribute 'new_scheduler'
ERROR: test_overrun_is_logged (test_build_task.Scheduler.test_overrun_is_logged)
AttributeError: module 'lab_13_nonblocking_scheduler' has no attribute 'new_scheduler'
ERROR: test_sensor_keeps_its_period (test_build_task.Scheduler.test_sensor_keeps_its_period)
AttributeError: module 'lab_13_nonblocking_scheduler' has no attribute 'new_scheduler'
FAIL: test_every_quick_tap_counts (test_build_task.Scheduler.test_every_quick_tap_counts)
AssertionError: 1 != 8
Ran 6 tests in 0.016s
FAILED (failures=1, errors=5)
```
Observed with `solution.py`:
```
test_every_quick_tap_counts (test_build_task.Scheduler.test_every_quick_tap_counts) ... ok
test_failing_task_leads_to_safe_state (test_build_task.Scheduler.test_failing_task_leads_to_safe_state) ... ok
test_long_press_still_clears (test_build_task.Scheduler.test_long_press_still_clears) ... ok
test_no_overruns_on_the_happy_path (test_build_task.Scheduler.test_no_overruns_on_the_happy_path) ... ok
test_overrun_is_logged (test_build_task.Scheduler.test_overrun_is_logged) ... ok
test_sensor_keeps_its_period (test_build_task.Scheduler.test_sensor_keeps_its_period) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.656s

OK
```
The overrun and safe-state tests read the scheduler's JSON lines, for example
`{"t":0,"event":"overrun","task":"sensor","budget":20,"ms":300}` and
`{"t":...,"event":"safe_state","task":"sensor"}`.

## All tests in this lab
```bash
python3 -m unittest -v       # Windows (PowerShell): py -m unittest -v
```
```
test_every_quick_tap_counts (test_build_task.Scheduler.test_every_quick_tap_counts) ... ok
test_failing_task_leads_to_safe_state (test_build_task.Scheduler.test_failing_task_leads_to_safe_state) ... ok
test_long_press_still_clears (test_build_task.Scheduler.test_long_press_still_clears) ... ok
test_no_overruns_on_the_happy_path (test_build_task.Scheduler.test_no_overruns_on_the_happy_path) ... ok
test_overrun_is_logged (test_build_task.Scheduler.test_overrun_is_logged) ... ok
test_sensor_keeps_its_period (test_build_task.Scheduler.test_sensor_keeps_its_period) ... ok
test_quick_taps_are_missed (test_fault.Symptom.test_quick_taps_are_missed) ... ok
test_deliberate_press_counts (test_main.HappyPath.test_deliberate_press_counts) ... ok
test_long_press_clears (test_main.HappyPath.test_long_press_clears) ... ok
test_sensor_line_is_json_once_per_second (test_main.HappyPath.test_sensor_line_is_json_once_per_second) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.274s

OK
```

## Step 6 — try it
```bash
python3 try_it.py
```
```
try 1: counted 6 of 8 | stats {'runs': 160, 'overruns': 0, 'missed': 0, 'errors': 0} | events none
try 2: counted 8 of 8 | stats {'runs': 440, 'overruns': 10, 'missed': 170, 'errors': 0} | events ['late', 'overrun']
```
