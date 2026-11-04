# 20 · Model comparison: a galaxy rotation curve with and without a dark-matter halo

This is a **synthetic** rotation curve shaped like NGC 3198 (Begeman 1989): 40 radii from 1 to 30 kpc, flat near 150 km/s, with 2–6 km/s errors. `compare.py` fits four mass models by weighted least squares:
- disk only (exponential disk, Freeman 1970);
- disk + cored halo;
- disk + NFW halo (Navarro, Frenk & White 1996);
- disk + cored halo + a cubic "wiggle" term.

It then **selects** one to publish, and measures three selection rules over 50 seeded galaxies.

Read the concept note first: `../../../content/concepts/L400/20-model-comparison.md`. Main lab: Python 3.12 + numpy only (`galaxy.py` has the mass models, with Bessel functions from series and integrals).

## Run
```bash
python compare.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L400\20-model-comparison` on Windows, `cd labs/L400/20-model-comparison` on macOS). It takes about 15 s (50 galaxies × 3 rules).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux)
Seeded, identical on every run.
```
{"model": "disk only", "k": 1, "chi2": 3267.95, "bic": 3271.64, "aic": 3269.95, "runs_z": -6.05, "params": [2.118]}
{"model": "disk + cored halo", "k": 3, "chi2": 43.24, "bic": 54.3, "aic": 49.24, "runs_z": -1.27, "params": [1.087, 2.109, 4.57]}
{"model": "disk + NFW halo", "k": 3, "chi2": 67.83, "bic": 78.9, "aic": 73.83, "runs_z": -1.27, "params": [0.801, 120.916, 8.884]}
{"model": "disk + halo + wiggles", "k": 6, "chi2": 40.63, "bic": 62.76, "aic": 52.63, "runs_z": 0.64, "params": [0.421, 16.35, 1.715, -6.637, 5.243, -2.308]}
select() picks: disk + halo + wiggles
{"option": "A chi2", "picks_over_50_datasets": {"disk + halo + wiggles": 50}}
{"option": "B BIC", "picks_over_50_datasets": {"disk + cored halo": 50}}
{"option": "C holdout R>20", "picks_over_50_datasets": {"disk + NFW halo": 5, "disk + cored halo": 43, "disk + halo + wiggles": 2}}
```

## Failure lab: break it, see it, fix it
- **Fault (shipped in `compare.py`):** `select()` publishes the model with the lowest χ². Six parameters always bend closer to the points, so the wiggle model wins on the published curve (40.63 against 43.24) and on all 50 seeded galaxies. Its "halo" (ρ0 = 16.35 × 10⁷ M☉/kpc³, r_c = 1.7 kpc) is unphysical.
- **Fix (your build task):** select by BIC = χ² + k ln n (`solution/compare.py`). This gives disk + cored halo (BIC 54.30 against 62.76) on 50/50 galaxies.
- **Proof:** `BUILD_TARGET=mine python -m unittest test_build_task test_fitness` gives 12 failures on the shipped file (both build-task tests, including 10 seed subtests, and the selection-rate fitness test) and passes on the solution. `TestFailureLab` in `test_compare.py` keeps the fault reproducible.

## Design decision and fitness function
- ADR: `decisions/0001-model-selection.md` chooses **B (BIC)** plus a runs test on the residuals. Over 50 galaxies, A picks wiggles 50/50, B picks the cored halo 50/50, and C (hold-out of R > 20 kpc) picks the cored halo 43, NFW 5 and wiggles 2.
- Fitness: `test_fitness.py` requires a halo model in at least 95 % of 50 galaxies, never the wiggles, published residuals with |runs Z| < 1.96, and disk only rejected (|Z| > 1.96). Observed: `Ran 2 tests ... OK`.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 10 tests ... OK (skipped=1)` - the SciPy Bessel cross-check is skipped locally (not installed) and runs in CI. Run 3× in a row: identical.

## Try it
```bash
python try_it.py
```
Observed:
```
1. NFW truth -> BIC picks disk + NFW halo {'disk only': 4281.27, 'disk + cored halo': 74.95, 'disk + NFW halo': 47.84, 'disk + halo + wiggles': 64.97}
2. R <= 8 kpc -> disk + cored halo {'disk only': (92.21, 1.504), 'disk + cored halo': (12.5, 1.19)} (bic, mass-to-light)
```

## Build it (hardening task)
Change `select()` in `compare.py` so it penalises parameters.

Hints:
- `table()` already returns `bic` and `aic` for each model. Pick by `bic`.
- With n = 40, each parameter costs ln 40 ≈ 3.7 in χ². Ask yourself what the wiggles buy.

Check your file: `BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v` (PowerShell: `$env:BUILD_TARGET = "mine"`). Shipped file: `Ran 4 tests ... FAILED (failures=12)`; after the fix: `OK`.
Reference solution output (`python solution/compare.py`):
```
{"model": "disk only", "k": 1, "chi2": 3267.95, "bic": 3271.64, "aic": 3269.95, "runs_z": -6.05, "params": [2.118]}
{"model": "disk + cored halo", "k": 3, "chi2": 43.24, "bic": 54.3, "aic": 49.24, "runs_z": -1.27, "params": [1.087, 2.109, 4.57]}
{"model": "disk + NFW halo", "k": 3, "chi2": 67.83, "bic": 78.9, "aic": 73.83, "runs_z": -1.27, "params": [0.801, 120.916, 8.884]}
{"model": "disk + halo + wiggles", "k": 6, "chi2": 40.63, "bic": 62.76, "aic": 52.63, "runs_z": 0.64, "params": [0.421, 16.35, 1.715, -6.637, 5.243, -2.308]}
select() picks: disk + cored halo
{"option": "A chi2", "picks_over_50_datasets": {"disk + halo + wiggles": 50}}
{"option": "B BIC", "picks_over_50_datasets": {"disk + cored halo": 50}}
{"option": "C holdout R>20", "picks_over_50_datasets": {"disk + NFW halo": 5, "disk + cored halo": 43, "disk + halo + wiggles": 2}}
```

## Derived formula: the cored-halo rotation curve
Only the density ρ(r) = ρ0 / (1 + (r/rc)²) is taken from the literature (the cored form quoted by Navarro, Frenk & White 1996). The rotation curve is **derived here, not quoted**:
1. Enclosed mass: M(R) = ∫₀ᴿ 4π s² ρ(s) ds = 4π ρ0 ∫₀ᴿ s² / (1 + s²/rc²) ds.
2. Write s² / (1 + s²/rc²) = rc² [1 − 1 / (1 + s²/rc²)]. This integrates to rc² [R − rc arctan(R/rc)].
3. For a spherical mass, V² = G M(R) / R (shell theorem). So V² = 4π G ρ0 rc² [1 − (rc/R) arctan(R/rc)].

Limits: V rises roughly linearly for R ≪ rc, like a solid body, and flattens to V² → 4π G ρ0 rc² for R ≫ rc. `test_cored_halo_matches_numerical_mass_integral` compares the closed form with a numerical integral of the density. The exponential-disk curve (Freeman 1970) and the NFW curve (NFW 1996, eq. 5) are quoted from their papers.

## Library equivalent and real data (pending-ci)
- `bessel_scipy.py` compares our I0, I1, K0 and K1 with `scipy.special` on 200 points (relative error < 10⁻⁶ required).
- Real data: SPARC (Lelli, McGaugh & Schombert 2016) publishes NGC 3198's mass models, but its web page states no licence ("please cite the SPARC master paper"). The file is therefore not vendored; see KNOWN-GAPS for the manual path.

## Files
- `compare.py` - main lab code (ships the unfixed `select()`); `solution/compare.py` - the fix
- `galaxy.py` - disk, cored-halo and NFW models + seeded data; `bessel_scipy.py` - SciPy check (pending-ci)
- `decisions/0001-model-selection.md` - ADR; `test_fitness.py` - fitness function
- `try_it.py`; `test_compare.py` (unit tests + fault reproduction); `test_build_task.py`
