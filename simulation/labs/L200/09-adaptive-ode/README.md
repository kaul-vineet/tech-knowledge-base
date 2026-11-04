# 09 · ODE solvers in practice: adaptive steps, tolerances, stiffness

Compact Dormand-Prince RK45 with error control on coffee cooling, rabbits and foxes, and a stiff RC filter where an implicit method wins; SciPy solve_ivp in CI.

Read the concept note first: `../../../content/concepts/L200/09-adaptive-ode.md`. No new packages: the L100 pins (`labs/L100/01-setup-workbench/requirements.txt`) already include numpy, SciPy and SimPy.

## Run
```bash
python adaptive_ode.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L200\09-adaptive-ode` on Windows, `cd labs/L200/09-adaptive-ode` on macOS).

## Expected output (real run, Python 3.12.15, Linux; seeded, identical on every run)
```
1. coffee 90 C -> 30 min, room 20 C (exact 35.619111 C)
   rtol=1e-03:   5 steps, 0 rejected, error 1.3e-02 C
   rtol=1e-06:   9 steps, 0 rejected, error 8.2e-06 C
   rtol=1e-09:  26 steps, 0 rejected, error 7.9e-09 C
2. rabbits/foxes 0-15: 204 steps, invariant drift 2.6e-05
   smallest step 0.0316 at t=12.72: rabbits 12.24, foxes  1.12
   largest step 0.1852 at t= 7.40: rabbits  3.04, foxes  0.02
3. stiff RC filter (tau = 1 ms), 0-10 s, exact v(10)=-0.83961:
   explicit RK45 rtol=1e-03:  3027 steps (110 rejected), v(10)=-0.83987
   explicit RK45 rtol=1e-06:  3586 steps ( 10 rejected), v(10)=-0.83961
   implicit backward Euler dt=0.01: 1000 steps, v(10)=-0.83961
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 11 tests ... OK (skipped=2)` - library tests are skipped locally (not installed) and run in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
rabbits/foxes rtol=1e-03:   55 steps, invariant drift 1.4e-01
rabbits/foxes rtol=1e-06:  204 steps, invariant drift 2.6e-05
rabbits/foxes rtol=1e-09:  639 steps, invariant drift 3.1e-08
RC tau=1e-03 s: explicit RK45   3027 steps, v(10)=-0.83987
RC tau=1e-04 s: explicit RK45  30226 steps, v(10)=-0.83929
```

## Build it (your task)
Add event detection: solve_until(f, t0, y0, t_end, event) stops where event(t, y) changes sign (coffee reaches 60 C) and returns (t_event, y_event).

Hints:
- After each accepted step compare the sign of event at both ends.
- Bisect the step size from the start of that step until the bracket is < 1e-10.
- Return (None, y) if no sign change before t_end.

Check: `python -m unittest test_build_task -v` (observed: `Ran 3 tests ... OK`). The reference solution is `solution/ode_events.py`; to test your own version, change the import at the top of `test_build_task.py`.
Reference solution output (`python solution/ode_events.py`):
```
coffee reaches 60 C at t=11.192316 min (exact ln(70/40)/0.05 = 11.192316), T=60.000000 C
```

## Library equivalent (pending-ci)
`ode_scipy.py` does the same with SciPy 1.18.1 `solve_ivp` (RK45, Radau, BDF, LSODA, events). It is not installed in the offline sandbox, so it has **not been run yet**; the CI workflow installs the pinned version and runs it plus the un-skipped test.

## Files
- `adaptive_ode.py` - main lab code
- `ode_scipy.py` - SciPy 1.18.1 solve_ivp equivalent (pending-ci)
- `solution/ode_events.py` - buildTask solution
- `try_it.py` - tryIt script
- `test_*.py` - unit tests (`test_build_task.py` checks the buildTask)
