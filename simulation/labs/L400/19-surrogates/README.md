# 19 · Surrogate models and emulation: fit, validate on holdout, use for what-ifs, know where they stop

Thirty runs of an "expensive" simulation (the L200 lesson 8 clinic queue, 20,000 patients per run) train three cheap surrogates: a quadratic polynomial, a GP-lite (Gaussian process) and random Fourier features. Twenty fresh runs validate them. Then you ask what-if questions, including two just outside the training box, where every surrogate is confidently wrong. The exact Erlang C answer is the referee.

Read the concept note first: `../../../content/concepts/L400/19-surrogates.md`. Needs Python 3.12 + numpy.

## Run
```bash
python surrogate.py
```

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux) - shipped file
```
expensive model: M/M/3 DES, 20,000 patients/run; 30 LHS training runs, 20 holdout runs
surrogate        holdout RMSE max error   (min of wait)
polynomial              0.037     0.079
gp-lite                 0.042     0.103
random features         0.049     0.133
(noise floor)           0.033   = holdout runs vs Erlang C
gp-lite 95% intervals cover 85% of holdout runs; params {'length_scales': [0.4, 0.4], 'noise': 0.01}
WHAT-IF (Erlang C = exact answer for this M/M/3; * = answered by the simulation, not the surrogate):
  lam=2.00 mu=1.00 (rho 0.67): exact  0.444 | polynomial  0.466   gp-lite  0.447   random features  0.447  | gp sd 0.031
  lam=2.42 mu=1.00 (rho 0.81): exact  1.135 | polynomial  1.047   gp-lite  0.876   random features  0.833  | gp sd 0.052
  lam=2.70 mu=0.95 (rho 0.95): exact  6.015 | polynomial  1.930   gp-lite  0.877   random features  0.552  | gp sd 0.178
```

## Failure lab: break it, see it, fix it
- **Fault (seeded, shipped in `surrogate.py`):** `what_if()` answers every question with the surrogate. A +10% arrival rate (2.2 to 2.42/min) is just outside the training box (λ ≤ 2.4), and the GP says 0.876 against an exact 1.135 (-23%). At ρ = 0.95 every surrogate is off by a factor of 3 to 11. The GP's standard deviation (0.178) does not flag it.
- **Fix (your build task):** an envelope guard. Answer from the surrogate only inside the training box and when the GP's standard deviation is ≤ 0.10. Otherwise run the simulation (4 replications) and label the answer (`solution/surrogate.py`):
```
  lam=2.42 mu=1.00 (rho 0.81): exact  1.135 | polynomial  1.109*  gp-lite  1.109*  random features  1.109* | gp sd 0.052
  lam=2.70 mu=0.95 (rho 0.95): exact  6.015 | polynomial  6.240*  gp-lite  6.240*  random features  6.240* | gp sd 0.178
```
- **Proof:** `BUILD_TARGET=mine python -m unittest test_build_task` fails 2 of 3 on the shipped file (the in-box answer passes either way) and passes 3 of 3 on the solution. `TestFailureLab` keeps the extrapolation fault reproducible.

## Design decision and fitness function
Decision: `decisions/0001-gp-behind-envelope-guard.md`. All three surrogates sit at the simulation's noise floor (0.033). The GP is chosen because it reports uncertainty for a second in-box check, and the box guard does the real work. Fitness function `test_fitness.py`: GP holdout RMSE ≤ 0.06, 95% coverage ≥ 80%, in-box what-ifs within 10% of Erlang C, and no out-of-box answer from the surrogate. Observed: `Ran 3 tests ... OK` on the solution, and `FAILED (failures=1)` on the shipped file.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 10 tests ... OK` (test_surrogate 4, test_build_task 3, test_fitness 3; about 45 s here).

## Try it
```bash
python try_it.py
```
Observed:
```
n=30: polynomial 0.037  gp-lite 0.042  random features 0.049
n=10: polynomial 0.043  gp-lite 0.066  random features 0.181
polynomial: raw 1.930, log-fit 2.583, exact 6.015
gp-lite: raw 0.877, log-fit 0.929, exact 6.015
```
With 10 runs the flexible random-features model falls apart first. Fitting log(Wq) is a better output shape, but it still does not make extrapolation safe.

## Build it (design task)
Make `what_if(model, lam, mu)` in `surrogate.py` refuse to extrapolate. If (lam, mu) is outside `[LO, HI]`, or the model's standard deviation exceeds `SD_MAX = 0.10` (models without uncertainty return `None`), run `expensive()` `FALLBACK_REPS = 4` times on seeds 3000+ and return `"source": "simulation (outside envelope)"`.

Hints:
- `np.all((x >= LO) & (x <= HI))` is the box check.
- Keep the return shape the same (`lam`, `mu`, `Wq`, `source`), so callers can show where each answer came from.

Check: `BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v` (PowerShell: `$env:BUILD_TARGET = "mine"`).

## Library equivalent (pending-ci)
scikit-learn's `GaussianProcessRegressor` and `RBFSampler` and SciPy's `qmc.LatinHypercube` (SciPy 1.18) do the same jobs. They are listed as equivalents and not used: the lab stays numpy-only.

## Files
- `surrogate.py`: main lab (Latin hypercube, three surrogates, holdout, what-ifs). Ships the unfixed `what_if()`.
- `solution/surrogate.py`: buildTask solution (the envelope guard).
- `try_it.py`, `test_surrogate.py`, `test_build_task.py`, `test_fitness.py`.
- `decisions/0001-gp-behind-envelope-guard.md`: the ADR.
