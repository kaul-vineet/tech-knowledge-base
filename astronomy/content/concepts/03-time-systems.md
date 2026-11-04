**Concept: time scales for astronomy**

## Why it matters
Your log says 2026-10-29 15:30 UTC. An ephemeris wants TT, a periodogram wants days as one number, and pointing needs sidereal time. Mix them up and positions are wrong by up to a minute of time.

## Mental model
One moment, several clocks. Atomic clocks (TAI, TT) tick evenly; UTC follows Earth's rotation with leap seconds; sidereal time follows the stars.

```
UTC ──+leap seconds (37 s)──> TAI ──+32.184 s──> TT ──> JD(TT) for ephemerides
UTC ──> JD(UTC) ──USNO formula──> GMST ──+longitude/15──> LST
```

## How it works
1. **Julian Date is a running day count.** JD 2440587.5 is the Unix epoch, so JD = 2440587.5 + seconds/86400; 15:30 UTC gives 2461343.145833 → see lab step 2.
2. **Leap seconds are a table, not a formula.** TAI−UTC = 37 s since 2017-01-01 (IERS Bulletin C); TT−UTC = 69.184 s. J2000.0 (12:00 TT) is 11:58:55.816 UTC → see lab step 3.
3. **Sidereal time runs 1.0027 times faster.** The short USNO formula gives GMST 18h01m54.54s at 15:30 UTC. Checked against a published IAU 2006 worked example (2006-01-15), it lands 0.023 s from the official apparent sidereal time → see lab step 4.

## Common mistakes
- Hard-coding 37 s: the offset was 32 s in 2000 and may change after the table expires.
- Feeding UTC to code that expects TT (69 s error).
- Treating a sidereal day as 24 hours: it is 23h56m04s.
