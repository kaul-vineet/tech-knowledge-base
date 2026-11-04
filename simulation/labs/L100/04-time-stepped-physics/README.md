# 04 · Time-stepped physics: a parcel dropped from a drone

Step a falling 2 kg parcel with explicit Euler, semi-implicit Euler and RK4; compare with y = h - g t^2/2, then add drag.

Read the concept note first: `../../../content/concepts/04-time-stepped-physics.md`.

## Run
```bash
python falling.py
```

## Expected output (real run, Python 3.12.15, Linux; deterministic, no randomness, identical on every run)
```
No drag, height at t=3 s. Exact = 55.9000 m
    dt   explicit Euler err   semi-implicit err   RK4 err   (err = simulated - exact)
   0.1            +1.470000           -1.470000   -1.4e-14
  0.01            +0.147000           -0.147000   +7.8e-14
 0.001            +0.014700           -0.014700   +9.1e-13
With drag: terminal velocity = 18.40 m/s
Time to fall 100 m: no drag 4.52 s (exact 4.52 s), with drag 6.74 s, impact 18.37 m/s
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 6 tests ... OK (skipped=1)` - SciPy test skipped locally (not installed); runs in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
Euler dt=0.5: ground at 7.00 s, impact 18.40 m/s
RK4 dt=0.001: ground at 6.74 s, impact 18.37 m/s
4 kg parcel: terminal velocity 26.02 m/s (x1.41), ground at 5.65 s
sqrt(2) = 1.414
```

## Library equivalent (pending-ci)
`falling_scipy.py` does the same with the library. It is not installed in the offline sandbox, so it has **not been run yet**; the CI workflow installs the pinned version and runs it plus the un-skipped test.

## Files
- `falling.py` - main lab code
- `falling_scipy.py` - SciPy 1.18.1 solve_ivp equivalent (pending-ci)
- `test_falling.py` - tests incl. tanh cross-check; SciPy test skipped locally
- `try_it.py` - tryIt script
