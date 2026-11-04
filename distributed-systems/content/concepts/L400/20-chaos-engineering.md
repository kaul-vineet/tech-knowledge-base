## Why it matters
Lessons 12-16 hardened a saga, a Raft log, tracing and load shedding, each against the fault its lab injected. Production will combine faults nobody listed: a courier API outage during a deploy, a rolling restart that moves faster than replication. Chaos engineering is the discipline of finding those weaknesses on purpose, with experiments, before customers do (Basiri et al., 2016; Principles of Chaos). The catch: an experiment that finds a weakness has, by definition, hurt someone.

## Mental model
An experiment is a hypothesis test about steady state, not "breaking things":

```
steady state (measured output)   harmed orders = 0 | lost commits = 0, no-leader gap <= 40 ticks
hypothesis                        it stays so in the experiment group, like in the control group
variable (real-world event)       courier outage | crash after charge | node crash | fast rolling restart
blast radius                      10% stable cohort; abort after the first harmed order
verdict                           held (more confidence) or refuted (a target for improvement)
```

## Design space
- **Where**: production traffic gives the most realistic answers; staging and simulation are safer and repeatable. The lab runs seeded simulations of the L300 services, so every finding replays.
- **Which faults**: random faults (crash a random node) are cheap; correlated, operational events (rolling restarts, dependency outages) find different bugs. Prioritise by impact or frequency.
- **How bounded**: fault everything; or a cohort with a control group; plus an automatic abort on a steady-state breach.
- **How often**: manual game days versus an automated campaign in CI.

## How to decide
1. Pick a steady-state metric customers would notice, measured from the system's own data (the saga audit reads each service's records, not the orchestrator's opinion).
2. Write the hypothesis and the abort rule before you run.
3. Start with the smallest blast radius that can still refute the hypothesis; grow it only after it holds.
4. Run the campaign against both the old and the hardened version: a fault that refutes the old one and not the new one proves the fix.

Worked example (lab output, seed 14, 60 orders). Unbounded harness: the courier outage against the unhardened L300 saga refutes the hypothesis and **hurts 60 customers** (paid, not shipped, not refunded); crash-after-charge also hurts 60 (stranded sagas). Bounded harness (10% cohort, control group, abort after one): same verdict, **1 customer hurt**, control group 0 harmed. The hardened saga holds both hypotheses with 0 harmed. For Raft, 20 seeds of random single-node crashes found nothing in either version; a rolling restart that waits only 0-4 ticks between nodes lost committed entries in 1 of 20 seeds of the unhardened log, and 0 of 20 once the election restriction (L300 #12) is in. A patient rollout (20-30 ticks) also showed 0 of 20 - it hides the bug rather than fixing it. tryIt 1 separates the two protections: cohort only, 6 customers hurt; cohort plus abort, 1; 50% cohort without abort, 30.

## Failure modes at scale
- **The experiment becomes the outage**: no abort rule, or an abort that reads a lagging metric. Watch the experiment group's steady state per order, not a 5-minute average.
- **Cohort leakage**: faults that are not keyed by a stable cohort (shared caches, global config) reach the control group; the control group's harmed count is the alarm.
- **False confidence**: random faults hold for months while one operational sequence breaks everything. Review incidents and add their sequence as an experiment.
- **Rare findings**: a weakness that appears in 1 of 20 seeds needs many runs; small cohorts trade safety for detection time.

## Common mistakes
- Running faults without a written hypothesis and steady-state metric.
- No control group, so a bad deploy during the experiment is blamed on the fault (or the reverse).
- Treating "nothing broke" under random crashes as proof of safety.
