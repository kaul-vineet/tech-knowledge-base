# 19 · Big catalogues: sky indexing, cone-search performance and TAP/ADQL

A **synthetic** catalogue of 1 000 000 sources, uniform on the sphere, receives 600 cone searches of radius 0.1–1.0°. Fifty of the cones are near the poles and fifty straddle RA = 0/360. `catalog.py` compares three options against each other and against brute force:
- **A:** brute force, one dot product per source;
- **B:** declination zones 0.1° high, with a binary search on RA;
- **C:** the same zones 1.0° high.

It also prints the ADQL query that asks a TAP service the same question.

Read the concept note first: `../../../content/concepts/L400/19-big-catalogues.md`. Main lab: Python 3.12 + numpy only (about 40 MB of RAM for the catalogue).

## Run
```bash
python catalog.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L400\19-big-catalogues` on Windows, `cd labs/L400/19-big-catalogues` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux, 1 CPU)
`wrong_cones`, `sources_found` and `tested_per_query` are seeded and identical on every run. `build_s` and `ms_per_query` are wall-clock and vary.
```
{"option": "A brute force", "build_s": 0.17, "ms_per_query": 6.9032, "wrong_cones": 0, "sources_found": 16738, "tested_per_query": 1000000}
{"option": "B zones h=0.1", "build_s": 0.96, "ms_per_query": 0.3683, "wrong_cones": 374, "sources_found": 12765, "tested_per_query": 27}
{"option": "C zones h=1.0", "build_s": 0.68, "ms_per_query": 0.052, "wrong_cones": 374, "sources_found": 12765, "tested_per_query": 43}
SELECT source_id, ra, dec FROM gaiadr3.gaia_source WHERE 1 = CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 83.82, -5.39, 0.05))
```

## Failure lab: break it, see it, fix it
- **Fault (shipped in `catalog.py`):** `Zones.ra_windows()` searches RA ± r. Away from the equator a cone spans more than r in RA (about r/cos δ), over a pole it spans all RA, and at RA 0/360 the window wraps. As a result, 374 of 600 cones miss sources: 12 765 found instead of 16 738. Nothing crashes, and the answers are just short.
- **Fix (your build task):** use the exact half-width α = atan(sin r / √|cos(δ−r)·cos(δ+r)|), whole zones when |δ| + r ≥ 90°, and two windows across 0/360 (`solution/catalog.py`). The result is 0 wrong cones.
- **Proof:** `BUILD_TARGET=mine python -m unittest test_build_task test_fitness` fails on the shipped file (8 failures: 7 cone subtests plus the fitness exactness test) and passes on the solution. `TestFailureLab` in `test_catalog.py` keeps the fault reproducible (247 wrong cones on a 200 000-source catalogue).

## Design decision and fitness function
- ADR: `decisions/0001-catalogue-index.md` chooses **C**. In Python, the per-zone loop overhead outweighs the extra candidates: C tests about 62 sources per query and B about 39, yet C is faster.
- Fitness: `test_fitness.py` requires 0 wrong cones out of 600, a build under 10 s, and at least 10× faster than brute force (best of 3; generous wall-clock bounds). Observed: `Ran 3 tests ... OK`; run 3× in a row: OK, OK, OK.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 11 tests ... OK (skipped=2)` - the healpy and pyvo tests are skipped locally (not installed; pyvo also needs the network) and run in CI.

## Try it
```bash
python try_it.py
```
Observed (timings vary):
```
1. zones h=0.01: 1.877 ms/query (brute 6.16), wrong cones 0
1. zones h=1.0: 0.054 ms/query (brute 6.16), wrong cones 0
2. radius 5 deg: brute 8.16 ms, zones h=1.0 0.39 ms -> 21x, wrong 0
```

## Build it (hardening task)
Fix `Zones.ra_windows()` in `catalog.py` so the index returns exactly the brute-force answer for every cone.

Hints:
- If |dec| + r ≥ 90, the cone contains a pole: return `[(0.0, 360.0)]`.
- α = atan(sin r / √|cos(δ − r) · cos(δ + r)|), in degrees. It equals r at the equator and is about 2r at δ = 60°.
- If `ra − α < 0`, search `[ra − α + 360, 360]` and `[0, ra + α]`; do the same at the other end.

Check your file: `BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v` (PowerShell: `$env:BUILD_TARGET = "mine"`). Shipped file: `Ran 5 tests ... FAILED (failures=8)`; after the fix: `OK`.
Reference solution output (`python solution/catalog.py`, timings vary):
```
{"option": "A brute force", "build_s": 0.29, "ms_per_query": 8.5434, "wrong_cones": 0, "sources_found": 16738, "tested_per_query": 1000000}
{"option": "B zones h=0.1", "build_s": 0.69, "ms_per_query": 0.2891, "wrong_cones": 0, "sources_found": 16738, "tested_per_query": 39}
{"option": "C zones h=1.0", "build_s": 0.64, "ms_per_query": 0.1176, "wrong_cones": 0, "sources_found": 16738, "tested_per_query": 62}
SELECT source_id, ra, dec FROM gaiadr3.gaia_source WHERE 1 = CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 83.82, -5.39, 0.05))
```

## Library equivalents (pending-ci)
- `pyvo_query.py`: the same cone as ADQL 2.1 against the Gaia archive TAP service (`pyvo.dal.TAPService(...).run_sync(...)`). It needs the network. Gaia data are CC BY-NC 3.0 IGO: credit ESA/Gaia/DPAC.
- `healpix_check.py`: HEALPix candidates from `healpy.query_disc(nside=256, …, inclusive=True)` plus the same exact test. They must equal brute force. healpy publishes no Windows wheels, so this runs on macOS and Linux only.

## Files
- `catalog.py` - main lab code (ships the unfixed `ra_windows()`); `solution/catalog.py` - the fix
- `pyvo_query.py`, `healpix_check.py` - equivalents (pending-ci)
- `decisions/0001-catalogue-index.md` - ADR; `test_fitness.py` - fitness function
- `try_it.py`; `test_catalog.py` (unit tests + fault reproduction); `test_build_task.py`
