# Lab 14-power-budget — Power budgeting (modelled, not measured)

**Every current and battery figure here is an ESTIMATE.** Nothing was measured on a board. Sources
and labels (UPPER BOUND, BOARD SLEEP FLOOR, CHIP ONLY, ASSUMPTION) are next to each figure in `budget.py`.
**The headline battery life (`life_h`) is a board-level estimate at a conservative, assumed sleep floor
(0.5 mA), shown with a range (0.5–0.05 mA floor).** The chip-only figure (nRF52833 alone, 1.5 µA) is
printed separately as `chip_only_bound_h`: an outer bound the board cannot beat, never a board figure.

| File | Purpose |
|---|---|
| `main.py` | BEFORE: logs temperature every 100 ms with `log.add`, shows it, `sleep()` keeps the board in On mode |
| `solution.py` | AFTER (build task): adaptive interval (100 ms → 8 s while steady) + `power.deep_sleep(ms=...)` |
| `budget.py` | The model: runs a design for one simulated hour on a fixed temperature trace, prints one JSON line (samples, wake-ups, awake %, average mA, board life in hours + range, chip-only bound, worst detection delay, meets brief) |
| `test_main.py` | Logger rows, model arithmetic, one-hour averaging window, headline = conservative board figure, every figure labelled, JSON line shape |
| `test_fault.py` | The failureLab symptom: 41.7 h on 2 x AAA |
| `test_build_task.py` | Proof: fails on `main.py`, passes on `solution.py`; also pins the trade-off (a short spike is missed) |
| `try_it.py`, `try_it.json`, `test_try_it.py` | Two `tryIt` items (edit `solution.py` / `budget.py`) |
| `../../sim_stub/power.py` | Stub of the V2 `power` module (deep sleep moves the clock; no real power) |

## Figures used (sources in `budget.py`)
| Figure | Value | Label | Source |
|---|---|---|---|
| Board awake (On mode) | 30 mA | UPPER BOUND | micro:bit power-supply page: "worst case budget of 30mA for when all on-board peripherals are in use" |
| Board Deep Sleep floor (headline) | 0.5 mA (range 0.05–0.5) | BOARD SLEEP FLOOR, ASSUMPTION | not published for the board (interface MCU, regulator, sensors, pull-ups); conservative end used for `life_h`; measure it |
| Chip sleep floor (bound only) | 0.0015 mA | CHIP ONLY | nRF52833 PS: 1.5 µA System ON, wake on RTC; used only for `chip_only_bound_h` |
| Awake per wake-up | 20 ms | ASSUMPTION | not published; measure it |
| Battery | 1,250 mAh | rating | Energizer E92 (AAA) datasheet: 1,250 mAh at 25 mA to 0.8 V (older revision EBC-1103I; the current manufacturer sheet, https://data.energizer.com/pdfs/e92.pdf, shows capacity as a chart); two in series for 3 V |

## Step 1 — the logger (stub or simulator)
Paste `main.py` into the Python Editor: the display shows the temperature; the Data logging view (if
the simulator shows it) fills with rows. `harness/simulator-l300.spec.js` runs `solution.py` (which
needs the `power` module) and records any error — **pending-ci**.

## Steps 2-3 — run the model and see the failure
```bash
cd labs/L300/14-power-budget
python3 budget.py            # Windows (PowerShell): py budget.py
```
Observed (Python 3.12.15, Linux sandbox):
```
figures (estimates, see sources in the code): {'BOARD_ON_MA': 30.0, 'SLEEP_MA': 0.5, 'SLEEP_MA_LOW': 0.05, 'CHIP_SLEEP_MA': 0.0015, 'ACTIVE_MS': 20, 'BATTERY_MAH': 1250.0}
life_h = BOARD estimate at the conservative sleep floor; range = 0.5-0.05 mA floor; chip_only_bound_h is NOT a board figure
{"design": "main.py", "samples": 36000, "wakeups": 0, "max_delay_ms": 0, "meets_brief": false, "awake_pct": 100.0, "avg_ma": 30.0, "life_h": 41.7, "life_h_range": [41.7, 41.7], "chip_only_bound_h": 41.7}
{"design": "solution.py", "samples": 483, "wakeups": 483, "max_delay_ms": 4700, "meets_brief": true, "awake_pct": 0.27, "avg_ma": 0.5792, "life_h": 2158.3, "life_h_range": [2158.3, 9588.4], "chip_only_bound_h": 15244.7}
```
Read the adaptive design as **about 2,160 h (≈90 days) on the board estimate, 2,158–9,588 h across the
assumed floor range** — not 15,245 h, which is the chip alone. Even the conservative end meets the 720 h brief.

**Averaging window = exactly one hour.** 483 wake-ups × 20 ms = 9,660 ms awake in 3,600,000 ms, so at the
0.05 mA floor: (9,660 × 30 + 3,590,340 × 0.05) / 3,600,000 = 0.13037 mA → 1,250 / 0.13037 = 9,588.4 h. An earlier
version printed 9,600.5 h (and 2,158.9 / 15,275.4 h) because the last 8 s Deep Sleep, started at 3,599,400 ms, ran
the stub clock to 3,607,400 ms and that 7.4 s of extra sleep was averaged in. `run_design` now clips the run to the
window (`total_ms = run_ms`); `test_main.Model.test_window_is_exactly_one_hour` pins it.
```bash
python3 -m unittest -v test_fault
```
```
test_battery_lasts_hours_not_a_month (test_fault.Symptom.test_battery_lasts_hours_not_a_month) ... ok

----------------------------------------------------------------------
Ran 1 test in 1.745s

OK
```

## Steps 4-5 — build task: fails before, passes after
```bash
BUILD_FILE=main.py python3 -m unittest -v test_build_task          # macOS (zsh): BEFORE
$env:BUILD_FILE="main.py"; py -m unittest -v test_build_task      # Windows (PowerShell)
python3 -m unittest -v test_build_task                              # AFTER: solution.py
```
Observed with `main.py` (summary lines):
```
test_board_deep_sleeps_between_samples (test_build_task.Adaptive.test_board_deep_sleeps_between_samples) ... FAIL
test_interval_backs_off_and_resets (test_build_task.Adaptive.test_interval_backs_off_and_resets) ... ERROR
test_meets_the_brief (test_build_task.Adaptive.test_meets_the_brief) ... FAIL
test_tradeoff_short_spike_can_be_missed (test_build_task.Adaptive.test_tradeoff_short_spike_can_be_missed) ... FAIL
ERROR: test_interval_backs_off_and_resets (test_build_task.Adaptive.test_interval_backs_off_and_resets)
AttributeError: module 'lab_14_power_budget' has no attribute 'MIN_MS'
FAIL: test_board_deep_sleeps_between_samples (test_build_task.Adaptive.test_board_deep_sleeps_between_samples)
AssertionError: 0 != 600
FAIL: test_meets_the_brief (test_build_task.Adaptive.test_meets_the_brief)
AssertionError: False is not true : {'design': 'main.py', 'samples': 36000, 'wakeups': 0, 'max_delay_ms': 0, 'meets_brief': False, 'awake_pct': 100.0, 'avg_ma': 30.0, 'life_h': 41.7, 'life_h_range': [41.7, 41.7], 'chip_only_bound_h': 41.7}
FAIL: test_tradeoff_short_spike_can_be_missed (test_build_task.Adaptive.test_tradeoff_short_spike_can_be_missed)
AssertionError: True is not false : the spike was sampled
Ran 4 tests in 1.462s
FAILED (failures=3, errors=1)
```
Observed with `solution.py`:
```
test_board_deep_sleeps_between_samples (test_build_task.Adaptive.test_board_deep_sleeps_between_samples) ... ok
test_interval_backs_off_and_resets (test_build_task.Adaptive.test_interval_backs_off_and_resets) ... ok
test_meets_the_brief (test_build_task.Adaptive.test_meets_the_brief) ... ok
test_tradeoff_short_spike_can_be_missed (test_build_task.Adaptive.test_tradeoff_short_spike_can_be_missed) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.011s

OK
```

## All tests in this lab
```bash
python3 -m unittest -v
```
```
test_board_deep_sleeps_between_samples (test_build_task.Adaptive.test_board_deep_sleeps_between_samples) ... ok
test_interval_backs_off_and_resets (test_build_task.Adaptive.test_interval_backs_off_and_resets) ... ok
test_meets_the_brief (test_build_task.Adaptive.test_meets_the_brief) ... ok
test_tradeoff_short_spike_can_be_missed (test_build_task.Adaptive.test_tradeoff_short_spike_can_be_missed) ... ok
test_battery_lasts_hours_not_a_month (test_fault.Symptom.test_battery_lasts_hours_not_a_month) ... ok
test_logs_every_100_ms_and_shows_value (test_main.Logger.test_logs_every_100_ms_and_shows_value) ... ok
test_always_on_is_battery_over_current (test_main.Model.test_always_on_is_battery_over_current) ... ok
test_duty_cycle_average (test_main.Model.test_duty_cycle_average) ... ok
test_every_figure_is_labelled_in_the_source (test_main.Model.test_every_figure_is_labelled_in_the_source) ... ok
test_headline_is_the_conservative_board_figure (test_main.Model.test_headline_is_the_conservative_board_figure) ... ok
test_report_is_one_json_line (test_main.Model.test_report_is_one_json_line) ... ok
test_window_is_exactly_one_hour (test_main.Model.test_window_is_exactly_one_hour) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 14 tests in 6.295s

OK
```

## Step 6 — try it
```bash
python3 try_it.py
```
```
try 1: solution.py: avg 6.4 mA, life 195.3 h, meets brief False
try 2: main.py: avg 7.9 mA, life 158.2 h, meets brief False
```
Both still fail the brief: the sampling interval, not the sleep mode or the exact awake current,
decides the result.
