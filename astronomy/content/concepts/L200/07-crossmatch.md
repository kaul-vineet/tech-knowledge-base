**Concept: catalogue cross-matching**

## Why it matters
You have a source list and a survey catalogue and ask "which of my sources is which star?" With thousands of rows, comparing every pair is slow, and comparing RA and Dec as if they were x and y breaks near RA 0°/360° and near the poles.

## Mental model
Put every source on a unit sphere as a 3-D vector. "Close on the sky" becomes "close in 3-D", and a spatial index finds the nearest neighbour without checking everyone.

```
(RA, Dec) ──> (x, y, z) on the unit sphere ──> k-d tree of catalogue A
for each B source: nearest A ──> chord ≤ 2 sin(r/2) ? match : no match
```

## How it works
1. **Measure separations stably.** Vincenty's formula works for tiny and large angles; RA 359.9999° and 0.0001° at Dec 28° are 0.6357″ apart, not 360° → see lab step 5.
2. **Convert the radius to a chord.** On the unit sphere a 1″ angle is a straight-line distance 2 sin(0.5″), so Euclidean distance works → see lab step 2.
3. **Index with a k-d tree.** Split space alternately on x, y, z; skip a branch whose splitting plane is farther than the best match so far → see lab step 3.
4. **Decide what a match means.** Nearest-within-radius lets two B sources claim one A source (blends); one-to-one matching keeps only the closest claim → see lab steps 4 and 7.

**Worked example (lab run):** 2000 A sources, 2042 B sources, radius 1″. The tree needed 38,999 distance evaluations instead of 4,084,000. All 1812 true counterparts were found, median separation 0.233″; 25 A sources were claimed twice. One-to-one matching left 1817 pairs and lost 5 true counterparts to closer blends.

## Trade-offs
| Approach | Use when | Avoid when |
|---|---|---|
| Brute force | A few hundred rows, one-off check | Large catalogues (N × M grows fast) |
| k-d tree on unit vectors | Millions of rows in memory | Data does not fit in memory |
| Sky tiling (HEALPix) + database | Survey-scale catalogues, cone searches | Small local lists (overkill) |

## Common mistakes
- Subtracting RAs without wrapping at 360° or without the cos(Dec) factor.
- Choosing a radius much larger than the astrometric errors: false matches rise in crowded fields.
- Assuming nearest-neighbour matching is one-to-one.
