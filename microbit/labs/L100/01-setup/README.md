# Lab 01-setup — Set up: first program, serial panel, local tests

| File | Purpose |
|---|---|
| `main.py` | Lab program (flash/paste this into the simulator) |
| `test_main.py` | Unit tests: runs the lab logic against `labs/sim_stub` with injected inputs |
| `try_it.py`, `try_it.json`, `test_try_it.py` | The lesson's two `tryIt` items: code edits, a runner, and a test of the observed results |

## Run in the simulator
Paste `main.py` into python.microbit.org, press the simulator's play button, open the serial panel.

Simulator inputs used: none.

Expected serial in the simulator (from the program's `print` calls; checked automatically by
`harness/simulator.spec.js` in CI — **not yet observed**, status pending-ci):
```
hello from micro:bit
tick 1
tick 2
...
```

## Run the logic tests locally (no board, no internet)
```bash
# macOS (zsh) and Windows (PowerShell) alike; forward slashes work in both
cd labs/L100/01-setup
python3 -m unittest -v      # Windows (PowerShell): py -m unittest -v
```

### Expected output (observed in the sandbox, Python 3.12.15)
```
test_hello_shows_image_and_prints (test_main.SetupLab.test_hello_shows_image_and_prints) ... ok
test_step_counts_up (test_main.SetupLab.test_step_counts_up) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.009s

OK
```

## Try it (the lesson's `tryIt` items)
`try_it.json` holds the code edits; `try_it.py` applies them to `main.py` and runs
the result against the stub (`test_try_it.py` asserts the same results).
```bash
cd labs/L100/01-setup
python3 try_it.py            # Windows (PowerShell): py try_it.py
```
Observed in the sandbox (Python 3.12.15):
```
try 1: 'hello from micro:bit\ntick 1\ntick 2\ntick 3\ntick 4\n', running_time()=1000 ms
try 2: import returned=False, serial='hello from micro:bit\ntick 1\ntick 2\ntick 3\n'
```
In the simulator the same edits are checked by `harness/tryit.spec.js` — pending-ci, not yet observed.
