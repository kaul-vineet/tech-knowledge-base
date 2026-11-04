**Concept: observation planning - constraints, airmass and a scheduler you can trust**

## Why it matters
Telescope time is scarce. A night plan asks, for every target: is it dark, is the target high enough, is the Moon far enough away? A scheduler then packs the targets into the hours. A quietly wrong planner is worse than none: it points the telescope below the horizon, and nobody notices until the frames come back black.

## Mental model
A night is a timeline; each constraint masks it, and the scheduler packs blocks into what is left.

```
time  17:00 ........................................ 07:00
Sun   ######|----------- dark (Sun < -18 deg) -----------|####
Vega        |=====|      airmass <= 2 (alt >= ~30 deg)
Moon  Aldebaran: ------- < 30 deg from the full Moon all night -------
plan        [Deneb 60 min]    [Betelgeuse]  [Sirius]
```

## How it works
1. **Coordinates to altitude.** LST = GMST (USNO formula) + east longitude; hour angle = LST − RA; spherical trigonometry gives altitude and azimuth → see lab step 1.
2. **Darkness.** Astronomical twilight ends when the Sun's centre is 18° below the horizon (USNO definitions; civil −6°, nautical −12°). On the 10-minute grid, Gurgaon is dark from 18:50 to 05:20 on 2026-11-24 → see lab step 2.
3. **Airmass.** The path length through the atmosphere is X = sec z = 1/sin(alt) for a plane-parallel sky. Kasten & Young (1989) fit a curved, refracting standard atmosphere: X = 1/(sin h + 0.50572(h + 6.07995)^−1.6364), within 0.5 % of their table and finite (about 38) at the horizon → see lab step 4.
4. **Moon distance.** The great-circle separation is computed with the haversine form. A 30° limit removes Aldebaran (about 12° from the full Moon) and Capella → see lab step 2.
5. **Scheduling.** The greedy sequential rule starts, at each free step, the valid block with the lowest mean airmass (astroplan's SequentialScheduler fills time in order). An urgency rule instead starts the target that is about to set → see lab step 6.
6. **Check independently.** Recompute every block's altitude at start, middle and end → see lab step 3.

**Worked example (lab run):** the shipped sec z is −1.76 for Sirius at −34.6°. A negative number passes `airmass <= 2.0`, and "lowest wins" ranks it best, so 4 of 6 blocks point below the horizon. With airmass = ∞ below the horizon, the plan is Deneb 18:50, Betelgeuse 22:10 and Sirius 00:10. Urgency-first adds Altair at 18:50.

## Failure modes
- **Sign and domain errors.** The formula is correct above the horizon and absurd below it. You notice only with an independent re-check (`--check`) or a test that recomputes the altitude.
- **Greedy myopia.** Targets that stay up all night take the slots of targets that are setting; watch the unscheduled count.
- **Time zones.** Mixing local time and UT shifts the plan by 5.5 h at Gurgaon; keep datetimes timezone-aware.
- **Low-precision ephemerides.** The USNO Sun (about 1′) and Schlyter's Moon (1–2′) suffice for a 30° rule, not for occultations.

## Common mistakes
- Treating a constraint score as "smaller is better" without bounding its domain (astroplan's `AirmassConstraint` keeps `min=1`).
- Using J2000 coordinates near the poles or for precise pointing. Precession is about 0.36° by 2026, so let astropy transform the frames.
- Testing a scheduler only with its own helpers.
