**Concept: coordinates on the sky**

## Why it matters
A catalogue gives Vega as RA 279.23°, Dec +38.78°. Your observer in Gurgaon asks: "Is it up at 21:00, and where do I look?" Catalogue coordinates are fixed to the stars; the answer depends on place and time.

## Mental model
The sky is a globe turning over your head once per sidereal day. RA/Dec are latitude/longitude painted on the globe; Alt/Az are angles from your horizon.

```
RA, Dec ──(local sidereal time)──> hour angle H = LST − RA
H, Dec ──(your latitude)──> altitude, azimuth      up if altitude > 0
```

## How it works
1. **Sidereal time places the sky.** GMST from the Julian Date, plus longitude/15, gives local sidereal time: 23.1671 h in Gurgaon at 15:30 UTC on 2026-10-29 → see lab step 2.
2. **Hour angle + latitude give altitude and azimuth.** sin(alt) = sin δ sin φ + cos δ cos φ cos H. Deneb is at 56.27°, Sirius at −28.46° (below) → see lab step 3.
3. **The same formula works anywhere.** Change latitude/longitude and the table changes: from Greenwich at 21:00 UTC, Betelgeuse is just up (2.33°) → see lab step 4.

## Common mistakes
- Using local clock time (IST) where UTC is required.
- Forgetting that azimuth conventions differ (north-based here; some books count from south).
- Ignoring precession: this lab uses J2000 positions unprecessed; at about 50″ per year they drift about 0.4° by 2026, so a planetarium (positions of date) will differ slightly.
