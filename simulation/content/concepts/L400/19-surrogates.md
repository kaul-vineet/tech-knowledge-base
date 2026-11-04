**Concept: surrogate models (emulators) - cheap stand-ins that must know where they stop**

## Why it matters
A detailed simulation can take minutes per run. A capacity planner wants hundreds of what-ifs in a meeting. A surrogate (also called an emulator or metamodel) is a fast function fitted to a few expensive runs. It answers instantly. Inside the region it was trained on, it can be as good as the simulation itself. Outside that region it can be wrong by a factor of three while looking just as confident.

## Mental model
A surrogate is interpolation dressed up as a model. It knows only the box it was trained in.

```
expensive model f(lam, mu) --30 LHS runs--> fit s(lam, mu) --20 fresh runs--> holdout error
                                                 |
   what-if (lam, mu) --inside the box?--yes--> s(lam, mu)        (milliseconds)
                                    \--no---> run f (4 reps)       (seconds, honest)
```
Latin hypercube sampling (McKay, Beckman & Conover 1979) places exactly one point in each 1/n slice of every input, so 30 runs cover both inputs evenly.

## Design space
- **Quadratic polynomial (response surface).** It has 6 coefficients and is fitted by least squares. It is transparent and very cheap, and it is good when the response is smooth and gently curved. Its shape is fixed: it cannot bend more than a parabola, and it has no error bar.
- **GP-lite (Gaussian process).** It uses an RBF kernel, with length-scales and a noise nugget chosen by log marginal likelihood using the Cholesky recipe of Rasmussen & Williams' Algorithm 2.1. It fits any smooth shape and gives a predictive standard deviation. The cost is n³ to fit, and its uncertainty is only as good as its kernel assumptions.
- **Random Fourier features + ridge.** Use z(x) = √(2/D)·cos(Wx + b) (Rahimi & Recht 2007). This is a linear model that approximates a kernel machine and scales to many runs. It needs more data to settle and gives no error bar.

## How to decide
Criteria: holdout error compared with the simulation's own noise, honest uncertainty, cost, and behaviour at the edge of the box.

**Worked example (lab run).** The expensive model is the L200 M/M/3 clinic queue (20,000 patients per run), with λ in [1.5, 2.4] and μ in [0.95, 1.10]. On 20 holdout runs the RMSE was polynomial 0.037, GP-lite 0.042 and random features 0.049 min. The simulation's own noise against the exact Erlang C answer is 0.033. All three are at the noise floor, so accuracy cannot separate them. The GP's 95% intervals covered 85% of holdout runs. With only 10 runs, the random features fell apart (0.181) while the polynomial held (0.043). At λ = 2.42, just 1% outside the box, the GP said 0.876 against an exact 1.135. At ρ = 0.95 every surrogate failed, with 1.930, 0.877 and 0.552 against an exact 6.015, and the GP's standard deviation was only 0.178. **Decision (ADR 0001):** GP-lite behind an explicit envelope guard. Inside the training box the surrogate answers. Outside it, the guard runs the simulation (4 replications gave 6.240 at ρ = 0.95). The GP is preferred over the equally accurate polynomial because it reports uncertainty for the in-box second check (sd ≤ 0.10). `test_fitness.py` enforces holdout RMSE ≤ 0.06, coverage ≥ 80%, in-box what-ifs within 10% of Erlang C, and no out-of-box answer from the surrogate.

## Failure modes at scale
- **Extrapolation:** queue waits explode as ρ → 1, but every surrogate here flattened out. Fitting log(Wq) moved the polynomial from 1.930 only to 2.583 against an exact 6.015. A better output transform does not license extrapolation.
- **Overconfident GP:** a stationary kernel reverts to the mean far from data. Its standard deviation grows only to the prior scale, so "sd is small" is not proof of "inside".
- **Many inputs:** a box check is easy, but the convex hull of the training points is smaller than the box in high dimensions. A point can be inside the box and still far from every run.
- **n grows:** GP fitting costs n³. Beyond a few thousand runs, use random features or sparse GPs.

## Common mistakes
- Validating on the training runs, or reporting R² instead of holdout error compared with the noise floor.
- Answering what-ifs outside the design region without saying so.
- Using a first-10 slice of a 30-point Latin hypercube as if it were a 10-point one.
