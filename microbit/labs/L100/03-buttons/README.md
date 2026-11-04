# Lab 03-buttons — Buttons

| File | Purpose |
|---|---|
| `main.py` | Lab program (flash/paste this into the simulator) |
| `test_main.py` | Unit tests: runs the lab logic against `labs/sim_stub` with injected inputs |
| `try_it.py`, `try_it.json`, `test_try_it.py` | The lesson's two `tryIt` items: code edits, a runner, and a test of the observed results |

## Run in the simulator
Click A three times, then B. (Holding A and B at the same time may not be possible with one mouse; `test_both_held` covers that path.)

Simulator inputs used: buttonA, buttonB.

Expected serial in the simulator (from the program's `print` calls; checked automatically by
`harness/simulator.spec.js` in CI — **not yet observed**, status pending-ci):
```
A = +1, B = reset
count 1
count 2
count 3
count 0
```

## Run the logic tests locally (no board, no internet)
```bash
# macOS (zsh) and Windows (PowerShell) alike; forward slashes work in both
cd labs/L100/03-buttons
python3 -m unittest -v      # Windows (PowerShell): py -m unittest -v
```

### Expected output (observed in the sandbox, Python 3.12.15)
```
test_b_resets (test_main.ButtonsLab.test_b_resets) ... ok
test_both_held (test_main.ButtonsLab.test_both_held) ... ok
test_no_press_no_output (test_main.ButtonsLab.test_no_press_no_output) ... ok
test_three_presses_between_iterations_all_count (test_main.ButtonsLab.test_three_presses_between_iterations_all_count) ... ok
test_was_pressed_is_consumed (test_main.ButtonsLab.test_was_pressed_is_consumed) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.011s

OK
```

## Try it (the lesson's `tryIt` items)
`try_it.json` holds the code edits; `try_it.py` applies them to `main.py` and runs
the result against the stub (`test_try_it.py` asserts the same results).
```bash
cd labs/L100/03-buttons
python3 try_it.py            # Windows (PowerShell): py try_it.py
```
Observed in the sandbox (Python 3.12.15):
```
try 1: count=1, serial='count 1\n'
try 2: after 3 clicks: count=0 serial=''; held for 3 polls: count=3 serial='count 1\ncount 2\ncount 3\n'
```
In the simulator the same edits are checked by `harness/tryit.spec.js` — pending-ci, not yet observed.
