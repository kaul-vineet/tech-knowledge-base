# 26 · Ethics and responsibility: dark and quiet skies, observatory sites and open-data credit

The few numbers the lesson 26 case study needs: the magnitude-7 brightness recommendation as a flux ratio, when a satellite overhead enters Earth's shadow (cylindrical shadow, spherical Earth), and the licence-compatibility rule from lesson 21 applied to a Gaia-derived catalogue. The case analysis itself is written work; see content/L500.json.

Read the concept note first: `../../../content/concepts/L500/26-ethics-dark-skies.md`. Python 3.12 + numpy only (no extra packages).

## Run
```bash
python sky_numbers.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L500\26-ethics-dark-skies` on Windows, `cd labs/L500/26-ethics-dark-skies` on macOS). Runtime: instant.

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux; seeded, identical on every run)
```
mag 5 vs mag 7 satellite: 6.31x brighter; mag 4 vs 7: 15.85x
zenith satellite at  350 km: sunlit until the Sun is 18.6 deg below the horizon (into astronomical night)
zenith satellite at  550 km: sunlit until the Sun is 23.0 deg below the horizon (into astronomical night)
zenith satellite at 1200 km: sunlit until the Sun is 32.7 deg below the horizon (into astronomical night)
inputs ['CC-BY-NC-3.0-IGO'] -> release CC-BY-4.0: NOT OK (drops ['NC'])
inputs ['CC-BY-NC-3.0-IGO'] -> release CC-BY-NC-4.0: OK (keeps every input condition)
inputs ['CC-BY-NC-3.0-IGO', 'CC-BY-SA-4.0'] -> release CC-BY-NC-4.0: NOT OK (NC and SA inputs cannot both be honoured automatically - needs a person)
inputs ['CC0-1.0', 'CC-BY-4.0'] -> release CC-BY-4.0: OK (keeps every input condition)
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 3 tests ... OK`.

## How this is verified
`python research/l500_checks.py` (from the astronomy folder) re-runs every theorem check, compares it with the `checkOutput` recorded in `content/L500.json` (numbers within 2 units of the last printed digit), and recomputes every numeric answer in the problem sets.
