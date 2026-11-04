# Concept: Benchmarking honestly against classical solvers

## Why it matters
"Quantum beats classical" claims are cheap to make and expensive to believe. Most published QAOA wins on small
graphs disappear once the classical baseline gets the same budget, the same instances and the same number of
repetitions. Before your service offers a quantum solver, you need a comparison method that a sceptical colleague
cannot fault. The method matters more than any single result, so the method is what the fitness test guards.

## Mental model
A benchmark is an experiment with controlled inputs. Hold everything equal except the solver: the instance, the seed
list and the budget. Report a distribution, not the best run.

```
instance ─┬─▶ greedy    ─┐
seeds 0..9├─▶ annealing ─┼─▶ medians, success rate, TTS99 ─▶ code's decide() ─▶ winner
budget B ─┴─▶ QAOA p=1  ─┘        (exact optimum = the reference)
```

The budget unit here is a **sample**: one candidate bitstring evaluated. That is a classical single-flip evaluation or
one quantum shot. Time-to-solution is reported twice: as samples until the best cut first appeared, and as TTS99,
the number of samples needed for a 99 % chance of seeing the optimum at least once
(budget × ln 0.01 / ln(1 − success rate)).

## Design space
- **Exact enumeration.** It costs 2^n evaluations and proves optimality. At n = 12 that is 4096 evaluations in
  milliseconds. It is the reference and the yardstick for "is this problem even hard?".
- **Greedy local search** (best single flip, with restarts) and **simulated annealing** (Kirkpatrick et al. 1983:
  Metropolis flips on a cooling schedule) are cheap, strong baselines that scale to large graphs.
- **QAOA p = 1** (Farhi et al. 2014) on the simulator, charged like hardware: half the shots pick angles on a grid,
  half sample answers. The simulator's wall time grows as 2^n. It took 1.69 s per run at n = 16, against 0.001 s for
  greedy, and it says nothing about hardware time.

The forces: equal budgets, identical seeds, enough seeds to see variance, honest stopping rules, and a decision rule
written before the results are seen.

## How to decide
Criteria in order: median approximation ratio, success rate, then samples to the best cut. Ties go to the classical
baseline, because it is cheaper to run and to operate.

Worked example (fair harness, budget 200, 10 seeds, 3-regular graphs):
- n = 8: all three solvers succeed 10/10. Annealing wins on samples (33 versus greedy 36 versus QAOA 111).
- n = 12: QAOA wins with median ratio 0.9667, success 0.5 and TTS99 1329, against greedy's 0.9333, 0.4 and 1803.
- n = 16: greedy wins with success 0.9 and TTS99 400, against QAOA's 0.6 and 1005.

Then check how far the n = 12 win generalises. On five other 12-node graphs QAOA won once (try it 1). Exact
enumeration of n = 12 fits in 4096 evaluations, and with that budget all four solvers succeed (try it 2). The naive
method in `bench_lab.py` gave QAOA 4× the budget and its best of 10 seeds, while the baselines ran once at a quarter
budget. It reported a QAOA "win" at n = 12 that rests entirely on that unequal treatment. ADR 0001 records the
decision: solve exactly up to n = 20, and keep QAOA as a research option until it wins repeatedly, under noise and on
wall time.

## Failure modes at scale
- **Instance overfitting.** Tuning angles or schedules on the reported instance. The signal: the win vanishes on
  fresh seeds of the graph generator.
- **Hidden budget.** Angle training, calibration or classical post-processing that is not charged. The harness
  rejects any run whose `used` exceeds the budget.
- **Small-sample illusions.** With 10 seeds, 0.3 versus 0.5 success is within noise. Report intervals before claiming
  a ranking.
- **Simulator time as hardware time.** Statevector cost is 2^n. Hardware adds queueing (lesson 17) and noise (lesson 12).

## Common mistakes
- Reporting the best seed of the quantum solver against a single run of the baseline.
- Comparing against a weak baseline (random guessing, untuned annealing) instead of the strongest cheap one.
- Ignoring that exact enumeration answers every instance a simulator can hold.
