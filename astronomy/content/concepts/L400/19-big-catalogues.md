**Concept: big catalogues - sky indexes, exact cone searches, and the same question as ADQL**

## Why it matters
Every pipeline asks "what is already known near this position?": a cross-match against Gaia, a known-variable check for an alert, a calibration star list for a field. Gaia DR3 has about 1.8 billion rows. Testing every row for every query is fine for one question and hopeless for a million. An index makes it fast, and an index with a geometry bug makes it fast and **silently incomplete**. The answer looks plausible; it just misses sources near the poles or across RA = 0.

## Mental model
Cut the sphere into pieces you can find quickly, fetch only the pieces a cone can touch, then test the few candidates exactly.

```
dec +90 ------------------------------  zone z = floor((dec + 90) / h); rows sorted by (zone, RA)
        |  zone 172   [....RA window....]          cone (ra, dec, r):
        |  zone 171   [......RA window......]        zones z(dec - r) .. z(dec + r)
        |  zone 170   [....RA window....]            per zone: binary search RA in [ra - a, ra + a]
dec -90 ------------------------------               exact test: dot(xyz, cone) >= cos r
```

## Design space
- **Brute force.** One dot product per row is simple, exact and O(N) per query. It is the reference every index must match.
- **Declination zones** (Gray, Szalay et al. 2004). Zones of height h are sorted by RA, so a cone touches a few zones, and in each a binary search finds a narrow RA window. This works in plain numpy or on any B-tree index in SQL.
- **HEALPix** (Górski et al. 2005). Twelve base pixels subdivide into 12·Nside² equal-area cells. `healpy.query_disc` lists the cells a cone touches; HiPS and MOC build on it, and TAP services use HEALPix-like indexes. healpy has no Windows wheels.
- **Remote services.** When the data live in an archive, ask the question there: ADQL 2.1 over TAP 1.1 (pyvo), `1 = CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', ra0, dec0, r))`. TAP 1.1 removed the old `REQUEST=doQuery` parameter.

The forces are query time, build time and memory, and above all exactness. An index that returns fewer rows than brute force is a correctness bug, not a performance trade-off.

## How to decide
Make brute force the oracle and generate hard cones on purpose: near the poles, across RA = 0/360, and with large radii. Measure ms per query, how many candidates each option tests, and the build time.

**Worked example (lab run, 1 000 000 synthetic sources, 600 cones of 0.1–1.0°):**
- The shipped RA window (ra ± r) got **374 of 600 cones wrong**, finding 12 765 sources instead of 16 738. Away from the equator a cone spans about r/cos δ in RA, over a pole it spans all RA, and at 0/360 the window wraps.
- With the exact half-width α = atan(sin r / √|cos(δ−r) cos(δ+r)|), pole and wrap handling, and an exact test, both zone options give 0 wrong cones.
- Speed per query: brute force 6–11 ms (1 000 000 tested), h = 0.1° about 0.2–0.5 ms (39 tested), h = 1.0° about 0.05–0.14 ms (62 tested).

In Python the per-zone loop overhead outweighs the extra candidates, so coarse zones win. The ADR records that this depends on the query radius.

## Failure modes at scale
- **Very fine zones:** h = 0.01° took 1.3–1.8 ms per query in tryIt (two runs). The loop overhead per zone dominates, and the signal is ms/query rising while candidates fall.
- **Big cones:** at 5° the gain over brute force shrinks to about 17–31× (two runs). Cross-matching millions of positions needs a zone-against-zone join (sort both sides), not a query per source.
- **Memory:** about 40 MB per million rows here. At Gaia scale the index belongs in a database (zones, HEALPix or Q3C) behind TAP, and you query it remotely.
- **Coordinate drift:** cross-matching catalogues at different epochs without proper motion moves high-proper-motion stars outside small radii. Propagate positions first.

## Common mistakes
- Using an RA window of ±r, or Euclidean distance in (RA, Dec). Both are wrong away from the equator.
- Benchmarking only random cones. Uniform random cones rarely hit the poles or RA = 0, so seed the hard cases.
- Teaching old TAP syntax (`REQUEST=doQuery`) or depending on a remote service in unit tests. Keep network calls in a pending-CI equivalent.
