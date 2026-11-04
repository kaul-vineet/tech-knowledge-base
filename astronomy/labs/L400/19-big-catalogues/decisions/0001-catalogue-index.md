# 1. Index the catalogue by 1-degree declination zones and test every candidate exactly

## Status
Accepted (2026-10-29)

## Context
A pipeline cross-matches its detections against a 1 000 000-source all-sky catalogue (synthetic, uniform on the sphere). Queries are cones of radius 0.1–1.0°, and they appear anywhere: near the poles, and across RA = 0/360. Constraints:
- exactly the brute-force answer on every cone;
- a build of less than 10 s;
- at least 10× faster than brute force;
- numpy + stdlib only;
- an ADQL query that asks a TAP service the same question.

`catalog.py` (solution) measured three options on 600 test cones (50 near the poles, 50 across RA = 0). Times are wall-clock on 1 CPU and vary between runs:
- A, brute force (one dot product per source): about 6–11 ms per query, 1 000 000 sources tested.
- B, zones h = 0.1° with an RA binary search: about 0.2–0.5 ms per query, about 39 sources tested, 0 wrong cones.
- C, zones h = 1.0°: about 0.05–0.14 ms per query, about 62 sources tested, 0 wrong cones.

The shipped RA window (RA ± r, with no 1/cos Dec, no pole case and no wrap) got 374 of 600 cones wrong. Every one of them was missing sources.

## Decision
Use C: declination zones about as high as the typical query radius, with RA-sorted zones, exact RA half-width α = atan(sin r / √|cos(δ−r)·cos(δ+r)|), whole zones for cones over a pole, two windows across RA = 0, and an exact dot-product test on every candidate. Publish the same query as ADQL (`adql_cone()`): `1 = CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', …))`. Use pyvo for remote TAP services.

## Consequences
- In Python, per-zone loop overhead dominates the extra candidates. Fine zones (h = 0.01°) took 1.3–1.8 ms per query in tryIt (two runs), slower than coarse zones. The best h depends on the query radius, so re-measure if typical cones change.
- Big cones (5°) shrink the gain to about 17–31× (two runs). Cross-matching millions of positions needs a batched join (zones join zones), not one query per source.
- The index is in memory: 1 M sources × (3 float64 coordinates + RA + ID) ≈ 40 MB. At Gaia scale (1.8 billion rows), use a database with a spatial index (HEALPix or Q3C, as TAP services do) rather than this structure.
- HEALPix (healpy) is checked as an equivalent in CI on macOS and Linux only. healpy publishes no Windows wheels.
- Fitness function: `test_fitness.py` checks 0 wrong cones out of 600, a build under 10 s, and a speed-up of at least 10× over brute force (best of 3).
