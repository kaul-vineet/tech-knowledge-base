# 02 · Coordinates and the sky

Turn catalogue RA/Dec into altitude and azimuth for an observer in Gurgaon (and anywhere else) and decide which stars are up.

Read the concept note first: `../../../content/concepts/02-coordinates-sky.md`.

## Run
```bash
python sky.py
```
```bash
python sky.py --lat 51.4778 --lon -0.0015 --utc 2026-10-29T21:00
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L100\02-coordinates` on Windows, `cd labs/L100/02-coordinates` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux; deterministic, identical on every run)
`python sky.py`:
```
observer lat +28.46 lon +77.03 | 2026-10-29 15:30 UTC | JD 2461343.14583 | LST 23.1671 h
star        alt(deg)  az(deg)  up?
Deneb          56.27   310.07  UP
Altair         39.35   257.43  UP
Vega           33.52   299.71  UP
Fomalhaut      31.84   183.17  UP
Polaris        28.93     0.65  UP
Capella        18.97    47.24  UP
Betelgeuse     -6.27    78.05  below
Arcturus      -24.58   311.22  below
Sirius        -28.46    94.49  below
Canopus       -33.23   136.60  below
```
`python sky.py --lat 51.4778 --lon -0.0015 --utc 2026-10-29T21:00`:
```
observer lat +51.48 lon -0.00 | 2026-10-29 21:00 UTC | JD 2461343.37500 | LST 23.5468 h
star        alt(deg)  az(deg)  up?
Deneb          61.31   274.65  UP
Polaris        52.00     0.84  UP
Vega           38.62   286.48  UP
Capella        36.38    59.40  UP
Altair         27.98   247.23  UP
Fomalhaut       8.53   187.72  UP
Betelgeuse      2.33    81.02  UP
Arcturus      -10.88   321.15  below
Sirius        -24.22    86.64  below
Canopus       -44.90   123.45  below
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 12 tests ... OK (skipped=1)` - library comparisons are skipped locally (not installed) and run in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
15:30 UTC up: Deneb, Altair, Vega, Fomalhaut, Polaris, Capella
18:30 UTC up: Capella, Betelgeuse, Polaris, Deneb, Fomalhaut, Sirius, Vega
Canopus from Gurgaon: alt -33.23 deg az 136.60 deg
Canopus from Sydney: alt  59.20 deg az 138.16 deg
```

## Library equivalent (pending-ci)
`sky_astropy.py` compares with Astropy 8.0.2 AltAz (no refraction). Not installed offline, so it has **not been run**; CI runs it and the un-skipped test (tolerance 0.6 deg in altitude: J2000 vs apparent place).

## Agent assist (optional)
```bash
python agent_assist.py --fake   # deterministic fake model server
python agent_assist.py          # local Ollama at LOCAL_MODEL_URL
```
Observed with the fake server:
```
1. agent proposed: {"visible": ["Vega", "Altair", "Sirius", "Polaris", "Canopus"], "reason": "bright stars that are usually seen on autumn evenings"}
2. code decided (altitude > 0): up = ['Altair', 'Capella', 'Deneb', 'Fomalhaut', 'Polaris', 'Vega']
   overruled (agent said visible, code says below): ['Canopus', 'Sirius']; missed: ['Capella', 'Deneb', 'Fomalhaut']; unknown names: none
3. agent explained: Deneb is highest at 56.27 degrees altitude; Canopus is lowest at -33.23 degrees, well below the horizon. Sirius rises at about 22:40 local time.
4. code checked 4 quoted numbers: 2 match the table; UNVERIFIED (treat as the model's guess): 22, 40
```
The agent only proposes and explains. Code computes, decides and flags any quoted number that is not in the table. Tests: `python -m unittest test_agent_assist -v` (fake server only).

## Notes
**Accuracy limit - read this.** Star positions are approximate J2000.0 (ICRS) values, rounded, as listed by SIMBAD (not re-fetched here). `sky.py` does **not** precess them to the observing date. Precession moves coordinates by about 50″ per year (IAU 2006 precession; [Wallace & Capitaine 2006](https://syrte.obspm.fr/iau2006/aa06_459.IAU06prec.pdf), eq. 4: ψ̄ ≈ 5038″ per century), so by 2026 the RA/Dec of date differ from J2000 by up to about 0.37° (~0.4°). Nutation, aberration and refraction are ignored as well. That is fine for "is it above the horizon?" and for planning, not for pointing a telescope; `sky_astropy.py` (CI) applies all of them, hence its 0.6° tolerance. Check positions in Stellarium with the atmosphere off.

## Files
- `sky.py` - main lab code
- `sky_astropy.py` - Astropy 8.0.2 equivalent (pending-ci)
- `test_sky.py` - time, geometry and Gurgaon checks
- `agent_assist.py` - agent proposes visible stars; code decides and checks
- `test_agent_assist.py` - agent-assist tests (fake server only)
- `try_it.py` - tryIt script
- `labs/_shared/local_agent/` - vendored chat client + fake model server
