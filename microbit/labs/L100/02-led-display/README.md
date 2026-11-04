# Lab 02-led-display — The LED display

| File | Purpose |
|---|---|
| `main.py` | Lab program (flash/paste this into the simulator) |
| `test_main.py` | Unit tests: runs the lab logic against `labs/sim_stub` with injected inputs |
| `try_it.py`, `try_it.json`, `test_try_it.py` | The lesson's two `tryIt` items: code edits, a runner, and a test of the observed results |

## Run in the simulator
Run in the simulator and watch the LEDs: "Hi" scrolls, a heart, the diamond, then the whole display fades up 0→9 and repeats.

Simulator inputs used: none.

Expected serial in the simulator (from the program's `print` calls; checked automatically by
`harness/simulator.spec.js` in CI — **not yet observed**, status pending-ci):
```
intro done
brightness 0
brightness 1
...
brightness 9
brightness 0
...
```

## Run the logic tests locally (no board, no internet)
```bash
# macOS (zsh) and Windows (PowerShell) alike; forward slashes work in both
cd labs/L100/02-led-display
python3 -m unittest -v      # Windows (PowerShell): py -m unittest -v
```

### Expected output (observed in the sandbox, Python 3.12.15)
```
test_builtin_images_are_read_only (test_main.LedDisplayLab.test_builtin_images_are_read_only) ... ok
test_custom_image_pixels (test_main.LedDisplayLab.test_custom_image_pixels) ... ok
test_intro_sequence (test_main.LedDisplayLab.test_intro_sequence) ... ok
test_step_shows_level_and_wraps (test_main.LedDisplayLab.test_step_shows_level_and_wraps) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.023s

OK
```

## Try it (the lesson's `tryIt` items)
`try_it.json` holds the code edits; `try_it.py` applies them to `main.py` and runs
the result against the stub (`test_try_it.py` asserts the same results).
```bash
cd labs/L100/02-led-display
python3 try_it.py            # Windows (PowerShell): py try_it.py
```
Observed in the sandbox (Python 3.12.15):
```
try 1: lit=13, sum=101, centre=9
try 2: 0 1 2 3 4 0 1
```
In the simulator the same edits are checked by `harness/tryit.spec.js` — pending-ci, not yet observed.
