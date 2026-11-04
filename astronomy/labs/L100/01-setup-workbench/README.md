# 01 · Your astronomy workbench

Check Python 3.12 + numpy, see the pinned Astropy/Skyfield/SciPy/photutils versions CI installs, create offline data folders, install Stellarium as the sky simulator.

Read the concept note first: `../../../content/concepts/01-setup-astronomy-workbench.md`.

## Run
```bash
python check_env.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L100\01-setup-workbench` on Windows, `cd labs/L100/01-setup-workbench` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux; deterministic, identical on every run)
`python check_env.py`:
```
Python 3.12.15 on Linux x86_64
  numpy     pin 2.5.3   installed 2.5.3
  astropy   pin 8.0.2   not installed -> runs in CI
  skyfield  pin 1.55    not installed -> runs in CI
  scipy     pin 1.18.1  not installed -> runs in CI
  photutils pin 3.1.1   not installed -> runs in CI
data folders: data/raw, data/cache, data/derived
seed 42 stars (RA deg, mag): [(278.6242, 8.97), (157.9962, 2.94), (309.0953, 11.76)]
READY for local labs
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 5 tests ... OK`

## Try it
```bash
python try_it.py
```
Observed:
```
unseeded fields equal? False
seed 42 first star: (278.6242, 8.97) | seed 43 first star: (234.8277, 10.39)
```

## Notes
Install the pins with `python -m pip install --only-binary=:all: -r requirements.txt` (online). Local output above shows the offline sandbox, where only numpy is installed.

Stellarium: `brew install --cask stellarium` (Mac) or the installer from https://stellarium.org/ (Windows). Full workstation setup: `../../../../shared/WORKSTATION-SETUP.md`.

## Files
- `check_env.py` - main lab code
- `requirements.txt` - pins: numpy, astropy, skyfield, scipy, photutils
- `test_setup.py` - version, numpy, pins (incl. CRLF), folders, seeding
- `try_it.py` - tryIt script
