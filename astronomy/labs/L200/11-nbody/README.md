# 11 · N-body simulation

Integrate Sun + Earth + Jupiter for 12 years with Euler and leapfrog, compare energy drift and orbits, and move the system to the centre-of-mass frame.

Read the concept note first: `../../../content/concepts/L200/11-nbody.md`.

## Run
```bash
python nbody.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L200\11-nbody` on Windows, `cd labs/L200/11-nbody` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux; deterministic, identical on every run)
`python nbody.py`:
```
Euler    12 yr, dt=0.001 yr: |dE/E| = 1.24e-02, Earth-Sun distance 1.55347 au, centre of mass moved 0.0315 au
leapfrog 12 yr, dt=0.001 yr: |dE/E| = 1.22e-12, Earth-Sun distance 1.00000 au, centre of mass moved 0.0315 au
Jupiter period from Kepler's third law: 11.867 yr
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 10 tests ... OK (skipped=1)` - library comparisons are skipped locally (not installed) and run in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
dt=0.001  Euler   : |dE/E| = 1.24e-02, Earth-Sun 1.5535 au
dt=0.001  leapfrog: |dE/E| = 1.22e-12, Earth-Sun 1.0000 au
dt=0.01   Euler   : |dE/E| = 6.98e-02, Earth-Sun 3.7634 au
dt=0.01   leapfrog: |dE/E| = 1.98e-10, Earth-Sun 1.0000 au
Euler   : Earth ends 5.85e-01 au from its start
leapfrog: Earth ends 1.17e-14 au from its start
```

## Build it (your task)
Implement to_com_frame(pos, vel, m): subtract the mass-weighted mean position and velocity so the centre of mass sits at the origin with zero momentum.

Hints:
- Centre of mass: m @ pos / m.sum() (a 3-vector).
- Do the same for velocities (total momentum / total mass).
- Return new arrays; do not change the inputs in place.

Check: `python -m unittest test_build_task -v` checks `solution/` by default. To check **your** edited file:
```bash
BUILD_TARGET=mine python -m unittest test_build_task -v      # macOS / Linux
$env:BUILD_TARGET = "mine"; python -m unittest test_build_task -v   # Windows PowerShell
```
Observed on the shipped (unfinished) file: `Ran 3 tests ... FAILED (failures=3)`. The reference solution output (`python solution/nbody.py`):
```
Euler    12 yr, dt=0.001 yr: |dE/E| = 1.24e-02, Earth-Sun distance 1.55347 au, centre of mass moved 0.0000 au
leapfrog 12 yr, dt=0.001 yr: |dE/E| = 1.26e-12, Earth-Sun distance 1.00000 au, centre of mass moved 0.0000 au
Jupiter period from Kepler's third law: 11.867 yr
```

## Library equivalent (pending-ci)
`nbody_rebound.py` runs the same system with REBOUND 5.2.2 `leapfrog` and compares Earth's distance after 2 years. **Not run yet** (pending-ci; `pip install -r ../requirements.txt`).

## Notes
Units: au, years, solar masses (G = 4 pi^2). Initial conditions are illustrative circular orbits.

## Files
- `nbody.py` - main lab code (to_com_frame unfinished)
- `solution/nbody.py` - buildTask solution
- `nbody_rebound.py` - REBOUND 5.2.2 equivalent (pending-ci)
- `test_nbody.py` - Newton's laws, energy, reversibility
- `test_build_task.py` - buildTask check (BUILD_TARGET=mine switch)
- `try_it.py` - tryIt script
