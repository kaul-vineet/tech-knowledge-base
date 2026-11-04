# 15 · Co-simulation with FMI: master algorithm and communication step

A room unit (own RK4 solver) and a PI thermostat unit with an FMI-like interface, coupled by a fixed-step master that logs every communication step as JSON lines.

Read the concept note first: `../../../content/concepts/L300/15-cosimulation-fmi.md`. Main lab: Python 3.12 + numpy only. The library equivalents need the L300 pins: `python -m pip install -r ../requirements.txt` (same command on macOS and Windows; adds SALib 1.6.0 and FMPy 0.3.32 to the L100 pins).

## Run
```bash
python cosim.py
python cosim.py 60
```
The first command runs at the shipped `COMM_STEP_S`; the second at any step you give (seconds). Windows (PowerShell) and macOS (zsh) use the same commands from the lab folder (`cd labs\L300\15-cosimulation-fmi` on Windows, `cd labs/L300/15-cosimulation-fmi` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux)
Deterministic (no random numbers): identical on every run. `python cosim.py` (shipped `COMM_STEP_S = 900`):
```
{"h_s": 900, "last_hour_swing_C": 6.78, "last_hour_mean_error_C": 2.72, "heater_flips": 9}
  cosim_log_900s.jsonl: 24 lines; last 4:
    {"t_min": 300.0, "h_s": 900, "T_room": 22.755, "heater": 0.049}
    {"t_min": 315.0, "h_s": 900, "T_room": 19.086, "heater": 0.0}
    {"t_min": 330.0, "h_s": 900, "T_room": 15.97, "heater": 0.996}
    {"t_min": 345.0, "h_s": 900, "T_room": 18.834, "heater": 1.0}
```
`python cosim.py 60`:
```
{"h_s": 60, "last_hour_swing_C": 0.0, "last_hour_mean_error_C": 0.0, "heater_flips": 1}
  cosim_log_60s.jsonl: 360 lines; last 4:
    {"t_min": 356.0, "h_s": 60, "T_room": 21.0, "heater": 0.667}
    {"t_min": 357.0, "h_s": 60, "T_room": 21.0, "heater": 0.667}
    {"t_min": 358.0, "h_s": 60, "T_room": 21.0, "heater": 0.667}
    {"t_min": 359.0, "h_s": 60, "T_room": 21.0, "heater": 0.667}
```

## Observability: read the log
Each run writes one JSON line per communication step (`cosim_log_<h>s.jsonl`: t_min, h_s, T_room, heater) and prints one JSON summary line. Diagnose the 900 s run from the log alone: the heater alternates between ~0 and 1 while T_room swings around 21 C.

## Failure lab: break it, see it, fix it
- **Fault (shipped in `cosim.py`, deterministic):** `COMM_STEP_S = 900` 'to run faster': the controller acts on a temperature that is one step old and holds its output for 15 min. The log shows the heater jumping between ~0 and 1 and a 6.78 C swing in the last hour - it looks like a broken controller.
- **Fix (your build task):** a communication step below the stability bound. Theory for this loop (gain K = 12, tau = 1 h): stable only if h < tau ln(12/11) = 313 s. With 60 s it settles at 21.0 C, heater 0.667, swing 0.00 C (`solution/cosim.py`). Alternatives: Gauss-Seidel ordering (stable at 450 s, tryIt 2) or a lower gain.
- **Proof:** `test_build_task.py` - 2 of 2 tests FAIL with `BUILD_TARGET=mine` on the shipped file, 2 of 2 PASS on the solution. `TestFailureLab` in `test_cosim.py` keeps the physics reproducible at explicit steps (900 s: swing > 3 C, >= 5 flips; 60 s: swing < 0.2 C; stable at 0.75 x 313 s, oscillating at 1.15 x 313 s). `research/failure_proofs_L300.py`: shipped file FAIL, solution PASS.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 14 tests ... OK (skipped=2)` - library tests are skipped locally (not installed) and run in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
h=180 s: last-hour swing 0.00 C, heater flips 1
h=240 s: last-hour swing 0.01 C, heater flips 1
h=300 s: last-hour swing 1.57 C, heater flips 1
h=360 s: last-hour swing 2.42 C, heater flips 10
Gauss-Seidel h=450 s: {'h_s': 450, 'last_hour_swing_C': 0.0, 'last_hour_mean_error_C': 0.0, 'heater_flips': 0}
Gauss-Seidel h=900 s: {'h_s': 900, 'last_hour_swing_C': 2.81, 'last_hour_mean_error_C': 0.92, 'heater_flips': 14}
```

## Build it (hardening task)
Fix `COMM_STEP_S` in `cosim.py`: pick a communication step that keeps this loop stable, and justify it with the bound tau ln(K/(K-1)).

Hints:
- K = Kp x Q_max x R = 0.5 x 3000 x 0.008 = 12; tau = R x C = 1 h.
- Leave margin below 313 s: tryIt 1 shows 300 s already swings 1.57 C.

Check your file: `BUILD_TARGET=mine python -m unittest test_build_task -v` (PowerShell: `$env:BUILD_TARGET = "mine"`, then `python -m unittest test_build_task -v`). Shipped file: `Ran 2 tests ... FAILED (failures=2)`; after the fix: `OK`. Without the variable the test checks `solution/cosim.py` (observed: `Ran 2 tests ... OK`).
Reference solution output (`python solution/cosim.py`) is the `python cosim.py 60` output above; its log goes to `solution/cosim_log_60s.jsonl`.

## Stretch (after the build task)
Add run_guarded(): run, read the health metrics from the log, halve the communication step while the loop oscillates, give up below a minimum step, and log every decision as a JSON line.

Hints:
- metrics() already computes last_hour_swing_C and heater_flips.
- Halve, do not shrink to the minimum at once: cost grows as 1/h.
- Stop with a 'gave_up' event rather than looping forever.

Check: `python -m unittest test_stretch -v` (observed: `Ran 3 tests ... OK`). The reference solution is `solution/guarded_master.py`; to test your own `guarded_master.py` in this folder, set `BUILD_TARGET=mine` (PowerShell: `$env:BUILD_TARGET = "mine"`).
Reference solution output (`python solution/guarded_master.py`):
```
{"event": "step_halved", "from_s": 900, "to_s": 450.0, "h_s": 900, "last_hour_swing_C": 6.78, "last_hour_mean_error_C": 2.72, "heater_flips": 9}
{"event": "step_halved", "from_s": 450.0, "to_s": 225.0, "h_s": 450.0, "last_hour_swing_C": 3.14, "last_hour_mean_error_C": 1.19, "heater_flips": 15}
{"event": "accepted", "h_s": 225.0, "last_hour_swing_C": 0.0, "last_hour_mean_error_C": 0.0, "heater_flips": 1}
```

## Library equivalent (pending-ci)
FMPy equivalent: `RoomThermal.mo` is the same room in Modelica; export it with OpenModelica (`omc export_fmu.mos` or OMEdit File > Export > FMU, FMI 2.0 Co-Simulation), then `python fmpy_cosim.py RoomThermal.fmu` runs the same master with FMPy's `FMU2Slave` in place of `units.Room`. CI runs `python fmpy_cosim.py` (FMPy import + API check only); the FMU run is a manual step. Note: OpenModelica's default Co-Simulation solver is forward Euler with one step per communication step (CVODE is optional).

## Files
- `cosim.py` - main lab code: master algorithm + JSON-lines log (ships the unfixed `COMM_STEP_S = 900`)
- `units.py` - Room and Thermostat units with an FMI-like interface
- `RoomThermal.mo` - the room in Modelica, for OpenModelica FMU export
- `export_fmu.mos` - OpenModelica script: buildModelFMU(..., version="2.0", fmuType="cs")
- `fmpy_cosim.py` - FMPy equivalent (pending-ci / manual)
- `solution/cosim.py` - buildTask solution (the fix)
- `solution/guarded_master.py` - stretch solution
- `try_it.py` - tryIt script
- `test_cosim.py` - unit tests + failure-lab physics
- `test_build_task.py` - buildTask check (`BUILD_TARGET=mine` checks your file)
- `test_stretch.py` - stretch check

