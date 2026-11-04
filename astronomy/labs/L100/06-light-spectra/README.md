# 06 · Light and spectra

Compute Planck curves, find their peaks numerically and with Wien's law, check Stefan-Boltzmann, and turn line shifts into velocities.

Read the concept note first: `../../../content/concepts/06-light-spectra.md`.

## Run
```bash
python light.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L100\06-light-spectra` on Windows, `cd labs/L100/06-light-spectra` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux; deterministic, identical on every run)
`python light.py`:
```
Sun              T=  5772 K  Wien b/T =   502.0 nm  numerical peak =   502.0 nm
Betelgeuse-like  T=  3600 K  Wien b/T =   804.9 nm  numerical peak =   804.9 nm
Rigel-like       T= 12100 K  Wien b/T =   239.5 nm  numerical peak =   239.5 nm
Sun: pi * integral B = 6.2939e+07 W/m^2 vs sigma T^4 = 6.2939e+07 W/m^2
H-alpha observed at 656.50 nm: v = +100.5 km/s (z = 0.000335)
z = 0.001: cz =       300 km/s  relativistic Doppler v =       300 km/s
z = 0.1  : cz =     29979 km/s  relativistic Doppler v =     28487 km/s
z = 1.0  : cz =    299792 km/s  relativistic Doppler v =    179875 km/s
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
T=5772 K: peak  502.0 nm, flux 6.294e+07 W/m^2
T=11544 K: peak  251.0 nm, flux 1.007e+09 W/m^2
z = 0.1000: cz = 29976 km/s, relativistic 28484 km/s
```

## Library equivalent (pending-ci)
`light_astropy.py` compares B_lambda at 500 nm with Astropy's BlackBody and recomputes b from CODATA constants. **Not run yet** (pending-ci).

## Files
- `light.py` - main lab code
- `light_astropy.py` - Astropy 8.0.2 BlackBody equivalent (pending-ci)
- `test_light.py` - Wien, Stefan-Boltzmann, Rayleigh-Jeans, Doppler
- `try_it.py` - tryIt script
