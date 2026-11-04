# 17 · Digital twins with live data: state estimation, drift detection, recalibration

A twin of one office zone, kept in step with a replayed sensor feed (JSON lines). A Kalman filter estimates the zone temperature and an unexplained heat gain. A CUSUM on the standardised innovations detects that the building has changed (a window left ajar from t = 2500 min). The alarm triggers a recalibration of the heat-loss and heater coefficients. You design the twin, compare three options with real numbers, and record the decision in an ADR.

Read the concept note first: `../../../content/concepts/L400/17-digital-twin.md`. Needs only Python 3.12 + numpy (same commands on macOS and Windows; `cd labs\L400\17-digital-twin` on Windows).

## Run
```bash
python make_feed.py      # optional: rewrites sensor_feed.jsonl (identical bytes; a test checks the hash)
python twin.py           # replays the feed, prints the options table, writes twin_log.jsonl
```

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux) - shipped file
```
OPTIONS (1-h forecast RMSE vs true zone temperature, C): before drift | last day
  A open-loop model       0.167 |  6.316
  B Kalman filter only    1.480 |  0.194
  C KF + CUSUM + refit    1.789 |  0.151
feed: 850 scored forecasts; skipped {'late_or_duplicate': 2, 'null_reading': 1}
events: 12 (twin_log.jsonl); first 3:
   {"t_min": 1250, "event": "drift_alarm", "s_hi": 405.13, "s_lo": 0.0}
   {"t_min": 1490, "event": "recalibrated", "a": 0.2, "b": 1.0}
   {"t_min": 1495, "event": "drift_alarm", "s_hi": 10.49, "s_lo": 0.0}
alarms before the drift (t < 2500 min): 5; first alarm after it: 2610 min
final model: a=0.0339 b=0.285 (plant after drift: a=0.035 b=0.30)
```

## Observability: read the log
`twin_log.jsonl` has one JSON line per twin event (`drift_alarm` with the CUSUM sums, `recalibrated` with the new a and b, `rejected` after the fix). In the shipped run the first line is an alarm at t_min 1250 with s_hi 405.13. That is not drift: it is the 85.0 °C glitch, assimilated as if it were real. After the fix (`solution/twin_log.jsonl`) the log has exactly three lines:
```
{"t_min": 1250, "event": "rejected", "zone_C": 85.0, "z": 404.5}
{"t_min": 2525, "event": "drift_alarm", "s_hi": 0.0, "s_lo": 10.51}
{"t_min": 2765, "event": "recalibrated", "a": 0.0331, "b": 0.267}
```

## Failure lab: break it, see it, fix it
- **Fault (seeded, shipped in `twin.py`):** `update()` assimilates every reading. The 85.0 °C glitch at t = 1250 drives the CUSUM to 405 and causes 5 false alarms before the drift. The resulting refit gives a = 0.2, b = 1.0 (the clip limits), and the before-drift RMSE is 1.789 °C.
- **Fix (your build task):** gate the innovation. If |ν|/√S > 5, log `rejected` and return before the state, history or CUSUM move (`solution/twin.py`). The result: 0 false alarms, an alarm 25 min after the drift, a = 0.0331, and a last-day RMSE of 0.127 °C.
- **Proof:** `BUILD_TARGET=mine python -m unittest test_build_task` fails 2 of 2 on the shipped file and passes on the solution. `TestFailureLab` in `test_twin.py` keeps the fault reproducible.

## Design decision and fitness function
Options are measured by `python solution/twin.py` (the first table): A open-loop 0.167 / 6.316, B Kalman filter only 0.189 / 0.194, C KF + CUSUM + refit 0.189 / 0.127 °C. Decision: `decisions/0001-twin-state-estimation.md` (option C). The fitness function `test_fitness.py` requires no false alarm, a detection delay ≤ 60 min, a recalibrated a within 15% of 0.035, and a last-day RMSE ≤ 0.15 °C that is also lower than option B's. Observed: `Ran 4 tests ... OK` on the solution, and `FAILED (failures=3)` with `BUILD_TARGET=mine` on the shipped file (the a-check passes either way).

## Test
```bash
python -m unittest -v
```
Observed: `Ran 12 tests ... OK` (test_twin 6, test_build_task 2 and test_fitness 4, both against the solution).

## Try it
```bash
python try_it.py
```
Observed:
```
h=8.0: false alarms 0, detection delay 25 min, rejected 1, last-day RMSE 0.127 C
h=4.0: false alarms 2, detection delay 760 min, rejected 490, last-day RMSE 2.407 C
gate=5.0: false alarms 0, detection delay 25 min, rejected 1, last-day RMSE 0.127 C
gate=2.5: false alarms 0, detection delay None min, rejected 366, last-day RMSE 6.051 C
```
A lower threshold gives false alarms, and a bad refit then locks the gate (490 rejections). A tight gate rejects the real change itself: the CUSUM never sees it, so the drift is never detected.

## Build it (design task)
Add an innovation gate to `Twin.update()` in `twin.py`: reject a reading whose standardised innovation exceeds `GATE = 5.0`, log it, and do not let it move the state, the refit history or the CUSUM.

Hints:
- `nu / sqrt(S)` is already computed as `zscore`. Gate before the Kalman update.
- Append `{"t_min": t, "event": "rejected", ...}` to `self.events` so the log shows what was dropped.

Check your file with `BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v` (PowerShell: `$env:BUILD_TARGET = "mine"`). The shipped file fails both; after your fix, both pass. Without the variable, the tests check `solution/twin.py`.

## Cross-links
- microbit L400 #20 (hardware-in-the-loop / live telemetry): a real micro:bit temperature stream could replace `sensor_feed.jsonl`, and the twin code would not change. See `seeAlso` in the lesson JSON.
- L300 #15 (co-simulation of the same kind of room model) and L300 #13 (calibration with a holdout) are the foundations.

## Files
- `twin.py`: main lab (Kalman filter, CUSUM, recalibration, options table). Ships the unfixed `update()`.
- `make_feed.py`: the seeded "real building" and its faulty feed. `sensor_feed.jsonl` is the committed replay.
- `solution/twin.py`: buildTask solution (the gate).
- `try_it.py`: the two tryIt experiments.
- `test_twin.py`: unit tests plus the fault reproduction. `test_build_task.py`: buildTask check. `test_fitness.py`: fitness function.
- `decisions/0001-twin-state-estimation.md`: the ADR.
