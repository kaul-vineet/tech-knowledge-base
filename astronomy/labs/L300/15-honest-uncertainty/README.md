# 15 · Fitting with honest uncertainty: least squares, bootstrap and MCMC for a transit

This is one transit in a **synthetic** light curve: 8 h at a 2-minute cadence, 1.0 % deep, 2.5 h long. The photometry pipeline reports `flux_err = 0.0010` per point, but the real scatter is 0.0020. `transit_fit.py` fits a trapezoid model by Levenberg–Marquardt and compares three kinds of error bar: the formal one, the bootstrap one, and the **coverage** over 200 seeded datasets. `mcmc.py` samples the posterior with the noise level as a free parameter.

Read the concept note first: `../../../content/concepts/L300/15-honest-uncertainty.md`. Main lab: Python 3.12 + numpy only. The emcee equivalent needs the L300 pins: `python -m pip install -r ../requirements.txt`.

## Run
```bash
python transit_fit.py
python mcmc.py
```
Windows (PowerShell) and macOS (zsh) use the same commands from the lab folder (`cd labs\L300\15-honest-uncertainty` on Windows, `cd labs/L300/15-honest-uncertainty` on macOS). `transit_fit.py` takes about 10 s (200 fits for the coverage, 300 for the bootstrap).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux)
Seeded, identical on every run.
```
{"param": "t0_h", "true": 0.12, "fit": 0.15667, "sigma_formal": 0.00601, "sigma_bootstrap": 0.0128}
{"param": "depth", "true": 0.01, "fit": 0.00963, "sigma_formal": 0.00013, "sigma_bootstrap": 0.00026}
{"param": "T14_h", "true": 2.5, "fit": 2.41574, "sigma_formal": 0.0256, "sigma_bootstrap": 0.04615}
{"param": "T12_h", "true": 0.3, "fit": 0.19103, "sigma_formal": 0.02184, "sigma_bootstrap": 0.04232}
reduced chi^2 with the reported flux_err: 4.13
1-sigma coverage over 200 seeded datasets: {'t0_h': 0.36, 'depth': 0.335, 'T14_h': 0.275, 'T12_h': 0.22}
```
```
{"param": "t0_h", "median": 0.15549, "minus": 0.01154, "plus": 0.01158}
{"param": "depth", "median": 0.00962, "minus": 0.00026, "plus": 0.00025}
{"param": "T14_h", "median": 2.36204, "minus": 0.08882, "plus": 0.07084}
{"param": "T12_h", "median": 0.15619, "minus": 0.06958, "plus": 0.05944}
{"param": "noise_scale_s", "median": 2.03536, "minus": 0.09109, "plus": 0.09312}
acceptance 0.270; autocorrelation time 35 steps; effective samples 430
```

## Failure lab: break it, see it, fix it
- **Fault (shipped in `transit_fit.py`):** `uncertainty()` computes cov = (JᵀWJ)⁻¹ with W = 1/flux_err², so it trusts the pipeline's 0.0010. The fit is fine, but every error bar is half its true size. The ±1σ interval contains the true mid-time in only 36 % of the 200 datasets (68 % expected), and the bootstrap σ(t0) is 0.0128 h against a formal 0.0060 h. The warning sign is printed: the reduced χ² is 4.13.
- **Fix (your build task):** scale the covariance by the reduced χ² (that is, let the residuals estimate σ) (`solution/transit_fit.py`). Coverage becomes t0 0.73 and depth 0.615, and the formal errors match the bootstrap.
- **What the fix does not fix:** T14 and T12 still cover only 0.555 / 0.56. The trapezoid has kinks, so linearised errors are too optimistic. The MCMC, which also samples the noise scale (s = 2.035 ± 0.09), gives T14 −0.089/+0.071 h instead of ±0.052 h.
- **Proof:** `test_build_task.py`. With `BUILD_TARGET=mine` on the shipped file, both tests fail; on the solution both pass. `TestFailureLab` in `test_transit_fit.py` keeps the fault reproducible (coverage [0.36, 0.335, 0.275, 0.22]).

## Test
```bash
python -m unittest -v
```
Observed: `Ran 10 tests ... OK (skipped=1)` (about 20 s) - the emcee test is skipped locally (not installed) and runs in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
1. flux_err = true scatter: coverage {'t0_h': 0.73, 'depth': 0.625, 'T14_h': 0.545, 'T12_h': 0.56}
2. 1000 steps: acceptance 0.277, tau 25, chain/tau 32 (emcee docs: > ~50 is often enough), s = 2.024
```

## Build it (hardening task)
Fix `uncertainty()` in `transit_fit.py` so the error bars cover the truth about 68 % of the time.

Hints:
- χ²_red = Σ(r/flux_err)² / (n − p) = 4.13 here. If the model is right, that means the real σ is √4.13 ≈ 2.03 × flux_err.
- Multiply the covariance by max(χ²_red, 1). Never shrink errors below the reported noise.

Check your file: `BUILD_TARGET=mine python -m unittest test_build_task -v` (PowerShell: `$env:BUILD_TARGET = "mine"`, then `python -m unittest test_build_task -v`). Shipped file: `Ran 2 tests ... FAILED (failures=2)`; after the fix: `OK`. Without the variable the test checks `solution/transit_fit.py` (observed: `Ran 2 tests ... OK`).
Reference solution output (`python solution/transit_fit.py`):
```
{"param": "t0_h", "true": 0.12, "fit": 0.15667, "sigma_formal": 0.01222, "sigma_bootstrap": 0.0128}
{"param": "depth", "true": 0.01, "fit": 0.00963, "sigma_formal": 0.00026, "sigma_bootstrap": 0.00026}
{"param": "T14_h", "true": 2.5, "fit": 2.41574, "sigma_formal": 0.05204, "sigma_bootstrap": 0.04615}
{"param": "T12_h", "true": 0.3, "fit": 0.19103, "sigma_formal": 0.0444, "sigma_bootstrap": 0.04232}
reduced chi^2 with the reported flux_err: 4.13
1-sigma coverage over 200 seeded datasets: {'t0_h': 0.73, 'depth': 0.615, 'T14_h': 0.555, 'T12_h': 0.56}
```

## Stretch (after the build task)
Report the MCMC result honestly. Quote median +plus −minus from the 16th, 50th and 84th percentiles, and flag a parameter as non-Gaussian when the plus and minus distances differ by more than 15 %.
Check: `python -m unittest test_stretch -v` (observed: `Ran 1 test ... OK`). Reference (`python solution/report.py`):
```
{"param": "t0_h", "median": 0.15549, "plus": 0.01158, "minus": 0.01154, "gaussian": true}
{"param": "depth", "median": 0.00962, "plus": 0.00025, "minus": 0.00026, "gaussian": true}
{"param": "T14_h", "median": 2.36204, "plus": 0.07084, "minus": 0.08882, "gaussian": false}
{"param": "T12_h", "median": 0.15619, "plus": 0.05944, "minus": 0.06958, "gaussian": false}
```

## Library equivalent (pending-ci)
`fit_emcee.py` samples the same `mcmc.log_prob` with `emcee.EnsembleSampler` (32 walkers, 4000 steps, `get_autocorr_time`). The test requires the median t0 to be within 0.004 h of 0.1555 and s within 0.15 of 2.0. It is skipped here and runs in CI.

## Files
- `transit_fit.py` - main lab code (ships the unfixed `uncertainty()`)
- `mcmc.py` - Metropolis sampler with a free noise scale + autocorrelation time
- `fit_emcee.py` - emcee equivalent (pending-ci)
- `solution/transit_fit.py` - buildTask solution; `solution/report.py` - stretch solution
- `try_it.py`; `test_transit_fit.py` (unit tests + fault reproduction); `test_build_task.py`; `test_stretch.py`
