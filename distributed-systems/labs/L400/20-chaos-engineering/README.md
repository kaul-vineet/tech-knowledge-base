# 20 · Chaos engineering: hypotheses, steady state, blast radius

Design question: how do we gain evidence that the L300 order saga (lesson 14) and replicated log (lesson 12) survive real-world faults - without the experiment itself hurting customers? Each experiment states a **steady-state metric** and a **hypothesis**, injects a seeded fault (courier API outage, orchestrator crash after a charge, random node crashes, a fast rolling restart) and tries to refute the hypothesis (Principles of Chaos). The targets are imported from `labs/L300` as shipped (unhardened) and as hardened by their build tasks.

Files: `chaos.py` (lesson: experiments, steady-state metric, campaign, summary) · `harness.py` (plumbing: loads the L300 labs with their own `helpers.py`, stable cohort hash, JSON lines) · `solution_chaos.py` (build task) · `test_chaos.py` · `test_build_task.py` · `test_fitness.py` · `ADR-020-bounded-chaos-campaign.md` · `try_it.py`.

## Run (Mac mini: `python3` inside the venv is `python`; Windows: same commands in PowerShell)
```bash
python chaos.py
```

## Expected output (real run, Python 3.12.15, Linux - identical on every run; seeded)
```
{"aborted": false, "blast_radius_pct": 100.0, "control_harmed": null, "customers_hurt": 60, "experiment": "saga/shipping-outage", "experiment_harmed": 60, "held": false, "seed": 14, "steady_state": "harmed orders = 0", "target": "L300 lesson"}
{"aborted": false, "blast_radius_pct": 100.0, "control_harmed": null, "customers_hurt": 60, "experiment": "saga/crash-after-charge", "experiment_harmed": 60, "held": false, "seed": 14, "steady_state": "harmed orders = 0", "target": "L300 lesson"}
{"aborted": false, "blast_radius_pct": 100.0, "control_harmed": null, "customers_hurt": 0, "experiment": "saga/shipping-outage", "experiment_harmed": 0, "held": true, "seed": 14, "steady_state": "harmed orders = 0", "target": "L300 hardened"}
{"aborted": false, "blast_radius_pct": 100.0, "control_harmed": null, "customers_hurt": 0, "experiment": "saga/crash-after-charge", "experiment_harmed": 0, "held": true, "seed": 14, "steady_state": "harmed orders = 0", "target": "L300 hardened"}
experiment              target          hypothesis held   customers hurt by the experiment
saga/shipping-outage    L300 lesson       0/1   runs           60
saga/crash-after-charge L300 lesson       0/1   runs           60
saga/shipping-outage    L300 hardened     1/1   runs            0
saga/crash-after-charge L300 hardened     1/1   runs            0
raft/random-crash       L300 lesson      20/20  runs            0
raft/rolling-restart    L300 lesson      19/20  runs            0
raft/random-crash       L300 hardened    20/20  runs            0
raft/rolling-restart    L300 hardened    20/20  runs            0
```
The findings are right - the unhardened saga keeps the money of unshipped orders and strands crashed sagas; random node crashes never broke the unhardened Raft, but a fast rolling restart (0-4 ticks between nodes) lost committed entries in 1 of 20 seeds. The **experiment is wrong**: the lesson harness injects the fault into every order with no control group and no abort, so finding the weakness hurt **60 customers**.

## Test
```bash
python -m unittest -v     # Ran 9 tests ... OK  (5 lesson + 2 build-task + 2 fitness, against the solution)
```

## Build task: bound the experiment
In `run_saga_experiment`: (1) inject only into a stable cohort of `BLAST_PCT` (10%) of orders (`harness.cohort`); (2) treat the other orders as the **control group** and report its harmed count; (3) **abort** - stop injecting - after `ABORT_AFTER` (1) harmed order. Before your change (real run): `Ran 2 tests in 10.279s / FAILED (failures=3)`. The reference prints:
```
{"aborted": true, "blast_radius_pct": 10.0, "control_harmed": 0, "customers_hurt": 1, "experiment": "saga/shipping-outage", "experiment_harmed": 1, "held": false, "seed": 14, "steady_state": "harmed orders = 0", "target": "L300 lesson"}
{"aborted": true, "blast_radius_pct": 10.0, "control_harmed": 0, "customers_hurt": 1, "experiment": "saga/crash-after-charge", "experiment_harmed": 1, "held": false, "seed": 14, "steady_state": "harmed orders = 0", "target": "L300 lesson"}
{"aborted": false, "blast_radius_pct": 10.0, "control_harmed": 0, "customers_hurt": 0, "experiment": "saga/shipping-outage", "experiment_harmed": 0, "held": true, "seed": 14, "steady_state": "harmed orders = 0", "target": "L300 hardened"}
{"aborted": false, "blast_radius_pct": 10.0, "control_harmed": 0, "customers_hurt": 0, "experiment": "saga/crash-after-charge", "experiment_harmed": 0, "held": true, "seed": 14, "steady_state": "harmed orders = 0", "target": "L300 hardened"}
```
Same finding (hypothesis refuted), one customer hurt instead of sixty, control group clean.

## Fitness function (keeps ADR-020 true)
`test_fitness.py`: every saga experiment stays within the 10% blast radius and hurts at most one customer, and the hardened L300 saga and Raft keep every hypothesis on seeds 14-16 - a regression in `labs/L300/.../solution_*.py` fails this lab's build.

## Try it (real run - `python try_it.py`)
```
tryIt 1: blast 10%, abort after 1 harmed order: customers hurt 1, hypothesis held False
tryIt 1: blast 10%, abort after never: customers hurt 6, hypothesis held False
tryIt 1: blast 50%, abort after never: customers hurt 30, hypothesis held False
tryIt 2: rolling restart, wait 0-4 ticks between nodes: L300 lesson Raft refuted in 1/20 seeds
tryIt 2: rolling restart, wait 20-30 ticks between nodes: L300 lesson Raft refuted in 0/20 seeds
```
tryIt 1: the blast radius alone limits harm to the cohort (6); the abort rule limits it to the first harmed order. tryIt 2: a patient rollout hides the Raft bug operationally - the code fix (L300 #12's election restriction) removes it.

## Platform notes
Pure computation on simulated time: no sockets, no sleeps, no files written. Seeded, so the output is identical on macOS, Windows and Linux (CI matrix pending).
