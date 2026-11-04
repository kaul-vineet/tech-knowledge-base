**Concept: Kepler orbits**

## Why it matters
You want Mars's position on a date without downloading an ephemeris. Six orbital elements and one equation give it to well under a degree, enough to plan an evening's observing or check a simulator.

## Mental model
Each planet moves on a fixed ellipse with the Sun at a focus; time along the orbit is uneven, so you convert "fraction of the period" into a position.

```
elements(T) ──> mean anomaly M ──Kepler: M = E − e sin E──> E ──> (x', y') in the orbit plane
──rotate by ω, I, Ω──> heliocentric ecliptic xyz ──minus Earth──> geocentric RA, Dec
```

## How it works
1. **Solve Kepler's equation with Newton's method.** Start at E = M + e sin M; four or five steps reach 1e-12: M = 1.0, e = 0.5 gives E = 1.498701133518 → see lab step 2.
2. **Rotate the orbit into space.** JPL's approximate elements (valid 1800–2050, Mars error about 40″) give Earth at r = 0.99346 au and Mars at 1.59098 au on 2026-10-29 → see lab step 3.
3. **Subtract Earth, then rotate to the equator.** Mars appears at RA 139.6593°, Dec +17.2889°, 1.4567 au away; Kepler's third law gives its period, 1.8808 yr → see lab step 4.

## Common mistakes
- Using degrees in `math.sin` (radians expected).
- Using elements outside their validity interval.
- Forgetting that a geocentric position needs Earth's position subtracted.
