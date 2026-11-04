# 04 · Units and scales

Build the distance ladder from exact definitions and convert between magnitudes, flux ratios and distances.

Read the concept note first: `../../../content/concepts/04-units-magnitudes.md`.

## Run
```bash
python units.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L100\04-units-magnitudes` on Windows, `cd labs/L100/04-units-magnitudes` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux; deterministic, identical on every run)
`python units.py`:
```
1 AU = 149597870700 m | 1 ly = 9460730472580800 m | 1 pc = 3.085678e+16 m
1 pc = 206264.806 AU = 3.2616 ly | light from 1 AU takes 499.005 s
5 mag brighter = x100.0 flux | 1 mag = x2.5119
flux x2 -> -0.7526 mag
star with M = 4.83 at   10 pc: m =   4.83 (distance modulus  0.00)
star with M = 4.83 at  100 pc: m =   9.83 (distance modulus  5.00)
star with M = 4.83 at 1000 pc: m =  14.83 (distance modulus 10.00)
same star at 1 AU (the Sun): m = -26.74
parallax 0.1 arcsec -> 10.0 pc; modulus 5.00 -> 100.0 pc
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 8 tests ... OK (skipped=1)` - library comparisons are skipped locally (not installed) and run in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
two m=6.0 stars together: m = 5.25
parallax 0.9 mas ->  1111.1 pc, distance modulus 10.229
parallax 1.0 mas ->  1000.0 pc, distance modulus 10.000
parallax 1.1 mas ->   909.1 pc, distance modulus 9.793
```

## Library equivalent (pending-ci)
`units_astropy.py` compares the constants and the distance modulus with Astropy 8.0.2 units. **Not run yet** (pending-ci).

## Files
- `units.py` - main lab code
- `units_astropy.py` - Astropy 8.0.2 units equivalent (pending-ci)
- `test_units.py` - definitions, magnitudes, round trips
- `try_it.py` - tryIt script
