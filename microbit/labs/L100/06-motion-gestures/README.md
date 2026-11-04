# Lab 06-motion-gestures — Motion and gestures

| File | Purpose |
|---|---|
| `main.py` | Lab program (flash/paste this into the simulator) |
| `test_main.py` | Unit tests: runs the lab logic against `labs/sim_stub` with injected inputs |
| `try_it.py`, `try_it.json`, `test_try_it.py` | The lesson's two `tryIt` items: code edits, a runner, and a test of the observed results |

## Run in the simulator
Expand the accelerometer panel, drag X to about 800, then choose 'shake' and press send.

Simulator inputs used: accelerometerX/Y/Z, gesture.

Expected serial in the simulator (from the program's `print` calls; checked automatically by
`harness/simulator.spec.js` in CI — **not yet observed**, status pending-ci):
```
x=0,y=0,z=-1024,tilt=flat,gesture=face up   (start values depend on the simulator)
x=800,...,tilt=right,...
shake!
```

## Run the logic tests locally (no board, no internet)
```bash
# macOS (zsh) and Windows (PowerShell) alike; forward slashes work in both
cd labs/L100/06-motion-gestures
python3 -m unittest -v      # Windows (PowerShell): py -m unittest -v
```

### Expected output (observed in the sandbox, Python 3.12.15)
```
test_flat_face_up (test_main.MotionLab.test_flat_face_up) ... ok
test_shake_reported_once (test_main.MotionLab.test_shake_reported_once) ... ok
test_tilt_right_shows_arrow (test_main.MotionLab.test_tilt_right_shows_arrow) ... ok
test_tilt_thresholds (test_main.MotionLab.test_tilt_thresholds) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.015s

OK
```

## Try it (the lesson's `tryIt` items)
`try_it.json` holds the code edits; `try_it.py` applies them to `main.py` and runs
the result against the stub (`test_try_it.py` asserts the same results).
```bash
cd labs/L100/06-motion-gestures
python3 try_it.py            # Windows (PowerShell): py try_it.py
```
Observed in the sandbox (Python 3.12.15):
```
try 1: x=200,y=0,z=-1024,tilt=right,gesture=
try 2: 'shake!' printed 3 time(s) in 3 polls
```
In the simulator the same edits are checked by `harness/tryit.spec.js` — pending-ci, not yet observed.
