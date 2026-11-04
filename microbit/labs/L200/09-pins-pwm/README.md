# Lab 09-pins-pwm — Pins and PWM on the edge connector

| File | Purpose |
|---|---|
| `main.py` | Lab program: logo toggle, A/B level, pin0 boost; pin1 digital out, pin2 PWM out |
| `test_main.py` | Unit tests: duty table, edge detection, levels, boost, pin modes (stub pins record outputs) |
| `solution.py` | Build task solution: potentiometer on pin0 (`read_analog`) sets the duty |
| `test_build_task.py` | Build task check; `BUILD_FILE=main.py` checks your own version |
| `try_it.py`, `try_it.json`, `test_try_it.py` | The lesson's two `tryIt` items |
| `../../sim_stub/` | Shared CPython stub: `microbit` (pins, i2c), `radio`, `log`, `i2c_devices` |

## Run in the simulator
1. Paste `main.py`, press play, open serial: `on=0,level=2,duty=0`.
2. Click the gold **logo** on the simulated board: `on=1,level=2,duty=511`.
3. Press **A**: `on=1,level=3,duty=767`. Press **B** to go down again.
4. Press the simulator's **pin 0** control (touch): `duty=1023` while held.

The simulator shows no voltage on pins 1 and 2: serial is the only output you can check there.
Analog input on pins is not available (README: "In future, analog values will be supported for
pins"), so the build task is checked on the stub only. Expected lines are from the `print` calls;
checked by `harness/simulator-l200.spec.js` — **not yet observed**, pending-ci.

## Run the logic tests locally (no board, no internet)
```bash
# macOS (zsh) and Windows (PowerShell) alike; forward slashes work in both
cd labs/L200/09-pins-pwm
python3 -m unittest -v      # Windows (PowerShell): py -m unittest -v
```

### Expected output (observed in the sandbox, Python 3.12.15, Linux)
```
test_duty_follows_pot (test_build_task.PotBuildTask.test_duty_follows_pot) ... ok
test_off_means_zero (test_build_task.PotBuildTask.test_off_means_zero) ... ok
test_buttons_change_level_with_limits (test_main.PinsLab.test_buttons_change_level_with_limits) ... ok
test_duty_levels (test_main.PinsLab.test_duty_levels) ... ok
test_logo_edge_toggles_once_while_held (test_main.PinsLab.test_logo_edge_toggles_once_while_held) ... ok
test_pin0_touch_boosts (test_main.PinsLab.test_pin0_touch_boosts) ... ok
test_starts_off (test_main.PinsLab.test_starts_off) ... ok
test_write_analog_rejects_out_of_range (test_main.PinsLab.test_write_analog_rejects_out_of_range) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.188s

OK
```
macOS and Windows: same tests in the CI matrix (`macos-latest`, `windows-latest`) — pending-ci.

## Build task
Potentiometer mode: with `USE_POT = True` the duty comes from `pin0.read_analog()` (0-1023) instead of A/B and the boost.
`solution.py` is a worked solution; `test_build_task.py` is the check. To check your own edit of `main.py`:
```bash
BUILD_FILE=main.py python3 -m unittest -v test_build_task              # macOS (zsh)
$env:BUILD_FILE="main.py"; py -m unittest -v test_build_task          # Windows (PowerShell)
```
Observed with `solution.py` (Python 3.12.15):
```
test_duty_follows_pot (test_build_task.PotBuildTask.test_duty_follows_pot) ... ok
test_off_means_zero (test_build_task.PotBuildTask.test_off_means_zero) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.043s

OK
```
(`main.py` as shipped fails this check on purpose: the feature is not there yet.)

## Try it (the lesson's `tryIt` items)
`try_it.json` holds the code edits; `try_it.py` applies them to `main.py` and runs the result on
the stub (`test_try_it.py` asserts the same results).
```bash
python3 try_it.py            # Windows (PowerShell): py try_it.py
```
Observed in the sandbox (Python 3.12.15):
```
try 1: on=1,level=2,duty=511 | on=0,level=2,duty=0 | on=1,level=2,duty=511
try 2: on=1,level=2,duty=682 | duty_for(0..3) = [0, 341, 682, 1023]
```
In the simulator, the items that can be observed through serial are checked by
`harness/tryit-l200.spec.js` — pending-ci, not yet observed.
