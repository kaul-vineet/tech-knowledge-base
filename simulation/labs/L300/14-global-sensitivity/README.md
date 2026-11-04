# 14 · Global sensitivity: OAT vs Morris vs Sobol'

Daily cooling energy of an office with four uncertain inputs; open windows only matter when outdoor and indoor temperatures differ (an interaction).

Read the concept note first: `../../../content/concepts/L300/14-global-sensitivity.md`. Main lab: Python 3.12 + numpy only. The library equivalents need the L300 pins: `python -m pip install -r ../requirements.txt` (same command on macOS and Windows; adds SALib 1.6.0 and FMPy 0.3.32 to the L100 pins).

## Run
```bash
python sensitivity.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L300\14-global-sensitivity` on Windows, `cd labs/L300/14-global-sensitivity` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux)
Seeded, identical on every run.
```
input         OAT swing   Morris mu*  sigma    Sobol S1    ST     (kWh/day; indices = share of variance)
outdoor_C        192.0      240.0   112.3     0.804    0.971
occupants         40.0       40.0     0.0     0.031    0.035
window_open        0.0      100.8   107.4     0.005    0.155
lights_h          12.0       12.0     0.0     0.004    0.003
runs: OAT 8, Morris 100, Sobol 49152
rank by OAT swing: outdoor_C > occupants > lights_h > window_open
rank by Sobol ST:  outdoor_C > window_open > occupants > lights_h
sum S1 = 0.844  (1 - sum S1 = variance from interactions)
screen() keeps ['outdoor_C', 'occupants']: the reduced model keeps 84.1% of the variance
```

## Failure lab: break it, see it, fix it
- **Fault (seeded, shipped in `sensitivity.py`):** `screen()` keeps the top 2 inputs by one-at-a-time swing: window_open swings 0.0 kWh around the nominal point (22 C outside = inside), so it is frozen at nominal. The reduced model keeps only 84.1% of the output variance, and nothing warns you.
- **Fix (your build task):** screen by Sobol' total-order index ST: window_open ST = 0.155 (S1 = 0.005: almost all of it is interaction). Keeping outdoor_C + window_open keeps 96.1% (`solution/sensitivity.py`).
- **Proof:** `test_build_task.py` - 2 of 2 tests FAIL with `BUILD_TARGET=mine` on the shipped file, 2 of 2 PASS on the solution. `TestFailureLab` in `test_sensitivity.py` keeps the fault reproducible (window dropped, < 88% kept). `research/failure_proofs_L300.py`: shipped file FAIL, solution PASS.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 16 tests ... OK (skipped=2)` - library tests are skipped locally (not installed) and run in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
OAT swings at outdoor=26 C: outdoor_C 192.0, occupants 40.0, window_open 96.0, lights_h 12.0
additive model: outdoor_C S1 0.952 ST 0.951, occupants S1 0.039 ST 0.041, window_open S1 0.000 ST 0.000, lights_h S1 0.005 ST 0.004; sum S1 = 0.995
```

## Build it (hardening task)
Fix `screen()` in `sensitivity.py` so it ranks inputs by a measure that includes interactions, then confirm with `variance_kept()`.

Hints:
- The table already holds S1 and ST for every input; which one counts interactions?
- Never trust a screen you have not checked: compare the reduced model's variance with the full model's.

Check your file: `BUILD_TARGET=mine python -m unittest test_build_task -v` (PowerShell: `$env:BUILD_TARGET = "mine"`, then `python -m unittest test_build_task -v`). Shipped file: `Ran 2 tests ... FAILED (failures=2)`; after the fix: `OK`. Without the variable the test checks `solution/sensitivity.py` (observed: `Ran 2 tests ... OK`).
Reference solution output (`python solution/sensitivity.py`), only the last line changes:
```
input         OAT swing   Morris mu*  sigma    Sobol S1    ST     (kWh/day; indices = share of variance)
outdoor_C        192.0      240.0   112.3     0.804    0.971
occupants         40.0       40.0     0.0     0.031    0.035
window_open        0.0      100.8   107.4     0.005    0.155
lights_h          12.0       12.0     0.0     0.004    0.003
runs: OAT 8, Morris 100, Sobol 49152
rank by OAT swing: outdoor_C > occupants > lights_h > window_open
rank by Sobol ST:  outdoor_C > window_open > occupants > lights_h
sum S1 = 0.844  (1 - sum S1 = variance from interactions)
screen() keeps ['outdoor_C', 'window_open']: the reduced model keeps 96.1% of the variance
```

## Stretch (after the build task)
Add st_with_ci() (bootstrap 95% intervals for ST from the same runs) and robust_ranking(), which writes '~' instead of '>' between inputs whose intervals overlap.

Hints:
- Resample the N rows of A, B and AB_i together - no new model runs.
- Use the 2.5th and 97.5th percentiles of 200 bootstrap ST values.
- Compare neighbours in the sorted order only.

Check: `python -m unittest test_stretch -v` (observed: `Ran 3 tests ... OK`). The reference solution is `solution/robust_ranking.py`; to test your own `robust_ranking.py` in this folder, set `BUILD_TARGET=mine` (PowerShell: `$env:BUILD_TARGET = "mine"`).
Reference solution output (`python solution/robust_ranking.py`):
```
N=   32: outdoor_C > window_open ~ occupants > lights_h
          ST 95% CI: outdoor_C 1.085 [0.546, 1.600], occupants 0.047 [0.029, 0.079], window_open 0.179 [0.069, 0.381], lights_h 0.003 [0.002, 0.005]
N= 8192: outdoor_C > window_open > occupants > lights_h
          ST 95% CI: outdoor_C 0.971 [0.943, 1.000], occupants 0.035 [0.034, 0.036], window_open 0.155 [0.149, 0.161], lights_h 0.003 [0.003, 0.003]
```

## Library equivalent (pending-ci)
`sensitivity_salib.py` runs SALib 1.6.0 (`sample.sobol.sample`, `analyze.sobol.analyze`, `sample.morris.sample`, `analyze.morris.analyze`); `test_sensitivity.py` requires ST within 0.03 of ours and Morris mu* of window_open above occupants. Skipped locally, runs in CI.

## Agent assist (optional)
A local model ranks the inputs from the sensitivity table; code ranks by ST, lists every disagreeing position and checks quoted numbers. `python agent_assist.py --fake` (drop `--fake` to use Ollama at `LOCAL_MODEL_URL`). Observed with the fake server:
```
1. code computed the table (input | oat_swing | mu* | sigma | S1 | ST):
   outdoor_C | 192.0 | 240.0 | 112.3 | 0.804 | 0.971
   occupants | 40.0 | 40.0 | 0.0 | 0.031 | 0.035
   window_open | 0.0 | 100.8 | 107.4 | 0.005 | 0.155
   lights_h | 12.0 | 12.0 | 0.0 | 0.004 | 0.003
2. agent ranked: outdoor_C > occupants > lights_h > window_open (window_open shows zero swing in the one-at-a-time test, so it can be ignored)
3. code ranks by ST: outdoor_C > window_open > occupants > lights_h
4. code verdict: OVERRULED at #2: agent occupants, code window_open; #3: agent lights_h, code occupants; #4: agent window_open, code lights_h
5. agent explained: outdoor_C dominates with a total-order index of 0.971. window_open explains about 30% of the variance, so it should stay in the model.
6. code checked 2 quoted numbers: 1 match; UNVERIFIED (treat as the model's guess): 30
```
Test: `python -m unittest test_agent_assist -v` (3 tests, fake server only).

## Files
- `sensitivity.py` - main lab code (OAT, Morris, Sobol'; ships the unfixed `screen()`)
- `sensitivity_salib.py` - SALib 1.6.0 equivalent (pending-ci)
- `agent_assist.py` - optional local-model ranking, checked by code
- `solution/sensitivity.py` - buildTask solution (the fix)
- `solution/robust_ranking.py` - stretch solution
- `try_it.py` - tryIt script
- `test_sensitivity.py` - unit tests vs analytic indices + fault reproduction
- `test_agent_assist.py` - agent assist tests (fake server)
- `test_build_task.py` - buildTask check (`BUILD_TARGET=mine` checks your file)
- `test_stretch.py` - stretch check

