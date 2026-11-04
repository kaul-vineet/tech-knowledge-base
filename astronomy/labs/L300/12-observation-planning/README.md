# 12 · Observation planning: airmass, twilight, Moon distance and a scheduler under constraints

One night at Gurgaon (28.46 N, 77.03 E), eight bright stars and three rules: astronomical darkness (Sun below −18°), airmass ≤ 2.0, at least 30° from the Moon. A greedy scheduler gives each star one 60-minute block. The night of 2026-11-24 has a full Moon next to Aldebaran.

Read the concept note first: `../../../content/concepts/L300/12-observation-planning.md`. Main lab: Python 3.12 + numpy only (`ephem.py` holds the USNO Sun/sidereal-time formulas and Schlyter's Moon). The astroplan equivalent needs the L300 pins: `python -m pip install -r ../requirements.txt` (same command on macOS and Windows).

## Run
```bash
python plan.py --check
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L300\12-observation-planning` on Windows, `cd labs/L300/12-observation-planning` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux)
Deterministic (no randomness; the grid is fixed).
```
Gurgaon, India 2026-11-24: astronomical darkness 18:50-05:20 local (10-min grid)
{"target": "Sirius", "start": "18:50", "alt_deg": -34.6, "airmass": -1.76, "moon_sep_deg": 59.5}
{"target": "Deneb", "start": "19:50", "alt_deg": 50.7, "airmass": 1.29, "moon_sep_deg": 84.0}
{"target": "Betelgeuse", "start": "22:10", "alt_deg": 31.5, "airmass": 1.92, "moon_sep_deg": 32.7}
{"target": "Vega", "start": "23:10", "alt_deg": -6.3, "airmass": -9.17, "moon_sep_deg": 106.2}
{"target": "Fomalhaut", "start": "00:10", "alt_deg": -3.2, "airmass": -18.11, "moon_sep_deg": 92.5}
{"target": "Altair", "start": "01:10", "alt_deg": -35.0, "airmass": -1.74, "moon_sep_deg": 115.9}
unscheduled: ['Aldebaran', 'Capella']
blocks below 30 deg altitude: ['Sirius', 'Vega', 'Fomalhaut', 'Altair']
```

## Failure lab: break it, see it, fix it
- **Fault (shipped in `plan.py`):** `airmass()` is the plane-parallel sec z = 1/sin(alt). Below the horizon it is **negative**, so `airmass <= 2.0` passes and the "lowest mean airmass wins" rule actively prefers stars under the ground: Sirius at −34.6° (airmass −1.76) gets the first block, then Vega, Fomalhaut and Altair below the horizon.
- **Fix (your build task):** make `airmass()` infinite at or below the horizon (astroplan's `AirmassConstraint` defaults to `min=1`, which also rejects a negative sec z) and use the Kasten & Young (1989) formula above it (`solution/plan.py`).
- **Proof:** `BUILD_TARGET=mine python -m unittest test_build_task` on the shipped file: 2 of 3 tests fail (15 subtest failures: 3 below-horizon altitudes and 4 buried targets × 3 times); on the solution all pass. `TestFailureLab` in `test_plan.py` keeps the fault reproducible.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 14 tests ... OK (skipped=1)` - the astroplan cross-check is skipped locally (not installed) and runs in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
1. Sydney dark 21:30-03:50 | scheduled ['Fomalhaut@21:30', 'Sirius@23:10', 'Betelgeuse@00:10'] | unscheduled ['Aldebaran', 'Altair', 'Capella', 'Deneb', 'Vega']
2. Gurgaon, Moon >= 45 deg | scheduled ['Deneb@18:50', 'Sirius@00:10'] | unscheduled ['Aldebaran', 'Altair', 'Betelgeuse', 'Capella', 'Fomalhaut', 'Vega']
```

## Build it (hardening task)
Fix `airmass()` in `plan.py` so a star at or below the horizon can never satisfy `airmass <= MAX_AIRMASS`.

Hints:
- Return `np.inf` where `alt <= 0`; the scheduler code does not need to change.
- Kasten & Young (1989, *Applied Optics* 28, 4735; [full text](https://archive.org/download/wikipedia-scholarly-sources-corpus/10.1364%252FAO.1.000024.zip/10.1364%252FAO.28.004735.pdf), [DOI 10.1364/AO.28.004735](https://doi.org/10.1364/AO.28.004735)), eq. 3 with their revised constants: X = 1/(sin h + 0.50572 (h + 6.07995°)^−1.6364), h in degrees. It reproduces their Table II (ISO standard atmosphere) to < 0.5 % - 1.9943 at 30° (table 1.9939; sec z gives 2.000) and 37.92 at the horizon (table 38.0868). `test_solution_airmass_matches_kasten_young_1989_table` checks nine table rows. The paper's argument is the *apparent* (refracted) elevation; the lab passes true elevation, which matters only within a few degrees of the horizon (KNOWN-GAPS).

Check your file: `BUILD_TARGET=mine python -m unittest test_build_task -v` (PowerShell: `$env:BUILD_TARGET = "mine"`, then `python -m unittest test_build_task -v`). Shipped file: `Ran 3 tests ... FAILED (failures=15)`; after the fix: `OK`. Without the variable the test checks `solution/plan.py` (observed: `Ran 3 tests ... OK`).
Reference solution output (`python solution/plan.py --check`):
```
Gurgaon, India 2026-11-24: astronomical darkness 18:50-05:20 local (10-min grid)
{"target": "Deneb", "start": "18:50", "alt_deg": 60.8, "airmass": 1.14, "moon_sep_deg": 83.7}
{"target": "Betelgeuse", "start": "22:10", "alt_deg": 31.5, "airmass": 1.91, "moon_sep_deg": 32.7}
{"target": "Sirius", "start": "00:10", "alt_deg": 30.2, "airmass": 1.98, "moon_sep_deg": 57.5}
unscheduled: ['Aldebaran', 'Altair', 'Capella', 'Fomalhaut', 'Vega']
blocks below 30 deg altitude: []
```

## Stretch (after the build task)
"Lowest airmass now" spends 18:50 on Deneb, which stays up all evening, while Altair sets. Schedule by urgency instead: at each free step, pick the valid target with the fewest remaining valid start steps (`solution/urgent.py`).
Check: `python -m unittest test_stretch -v` (observed: `Ran 1 test ... OK`); `BUILD_TARGET=mine` tests your own `urgent.py` in this folder.
Reference output (`python solution/urgent.py`):
```
{"target": "Altair", "start": "18:50", "alt_deg": 45.3, "airmass": 1.41, "moon_sep_deg": 112.7}
{"target": "Deneb", "start": "19:50", "alt_deg": 50.7, "airmass": 1.29, "moon_sep_deg": 84.0}
{"target": "Betelgeuse", "start": "22:10", "alt_deg": 31.5, "airmass": 1.91, "moon_sep_deg": 32.7}
{"target": "Sirius", "start": "00:10", "alt_deg": 30.2, "airmass": 1.98, "moon_sep_deg": 57.5}
unscheduled: ['Aldebaran', 'Capella', 'Fomalhaut', 'Vega']
```

## Library equivalent (pending-ci)
`plan_astroplan.py` runs the same night with astroplan 0.10.1 (`AtNightConstraint.twilight_astronomical()`, `AirmassConstraint(max=2.0)`, `MoonSeparationConstraint(min=30 deg)`, `SequentialScheduler`) and reports the largest altitude difference between `ephem.py` and astropy's `get_body` for the Sun (< 0.1° required) and the Moon (< 0.5°). Not run here.

## Files
- `plan.py` - main lab code (ships the unfixed `airmass()`)
- `ephem.py` - low-precision Sun, Moon, sidereal time, alt/az, separation
- `plan_astroplan.py` - astropy/astroplan equivalent (pending-ci)
- `solution/plan.py` - buildTask solution (the fix); `solution/urgent.py` - stretch solution
- `try_it.py` - tryIt script
- `test_plan.py` - unit tests + fault reproduction; `test_build_task.py` - buildTask check; `test_stretch.py` - stretch check
