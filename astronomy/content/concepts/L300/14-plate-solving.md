**Concept: plate solving - from pixel positions to sky coordinates with triangles, RANSAC and a TAN WCS**

## Why it matters
Before you can cross-match, stack or measure motion, an image needs a World Coordinate System (WCS). Mount pointing is good to a fraction of a degree; science needs a fraction of an arcsecond. A plate solver recognises the star pattern and fits the mapping. When it works near the equator but fails near the pole, the bug is usually in the projection, not the matching.

## Mental model
Shapes survive shift, rotation, scale and mirroring: match shapes first, fit the exact map second.

```
pixels (x, y) --triangles--> invariants (L2/L1, L1/L0) <--triangles-- catalogue on the TAN plane
        |                         match + vote                               ^
        +--- RANSAC: 3 pairs -> affine -> count agreeing pairs ----------------+
        +--- least squares on all matches -> CD matrix + CRVAL -> residuals (arcsec)
```

## How it works
1. **Invariants.** For a triangle with sides L2 ≥ L1 ≥ L0, the pair (L2/L1, L1/L0) does not depend on position, orientation or scale (astroalign; astrometry.net uses 4-star quads) → see lab step 2.
2. **Votes.** Every pair of triangles whose invariants agree within 0.8 % votes for three star correspondences. Spurious detections also collect votes → see lab step 2.
3. **Consensus.** Try every 3 voted pairs as an exact affine map and keep the map most pairs agree with (within 6″). Wrong pairs cannot outvote geometry → see lab step 3.
4. **Fit and refine.** Least squares maps pixels to the plane: plane = CD · (pixel − CRPIX) + offset. Transform all detections, re-match the nearest within 6″, and refit. A second pass puts the tangent point at the solved centre, so rotation refers to north there → see lab step 3.
5. **Project correctly.** The camera makes a gnomonic (TAN) image of the sphere (Calabretta & Greisen 2002). A degree of RA spans cos(Dec) degrees on the sky → see lab step 5.

**Worked example (lab run):** a test triangle at Dec −5.4° has invariants (1.049, 1.083) in raw RA/Dec offsets and (1.051, 1.078) on the TAN plane, a 0.4 % difference. At Dec +62.1° the TAN values are (1.097, 1.685), 36 % away. The shipped solver solves Orion (32 stars, rms 0.373″, scale 2.0045″/px) and fails on Cassiopeia. With TAN, both solve: Cassiopeia matches 23 stars, rms 0.503″, pointing error 0.05″, rotation −32.999° (true −33°).

## Failure modes
- **Equator-only success.** A missing cos(Dec), or flat offsets instead of a projection, passes every test taken near Dec 0. Test a field above |Dec| 60°.
- **Too loose a tolerance.** At TOL 0.05 there are as many votes, but only 3 pairs agree with the best geometry (8 at 0.008). Count the agreeing pairs, not the votes.
- **Hint too far off.** The catalogue window misses the field, so you get no solution at all. Search rings of hints (stretch), or solve blind like astrometry.net.
- **Accepting a bad solution.** Require enough matched stars and sub-arcsecond residuals (astrometry.net verifies with a Bayesian test).

## Common mistakes
- Mixing 0-based (numpy, astropy pixel) and 1-based (FITS) pixel coordinates. That is a 1-pixel shift everywhere.
- Fitting all voted pairs without rejecting outliers.
- Reporting rotation without saying where north is measured.
