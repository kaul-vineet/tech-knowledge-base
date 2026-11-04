# Team roles (capstone) and pair-programming protocol (L200)

## Capstone team roles (teams of 4; with 3, merge Integrator and Reviewer)

Roles rotate at the milestone boundary after M3, so everyone owns some modelling work and some engineering work. Every member must be able to explain all of the code in the oral defence (rubric: "Ownership of team work").

| Role | Owns | Milestones led | Hand-off artefact |
|---|---|---|---|
| **Modeller** | Input modelling, DES logic, calibration | M1-M3 | Fitted-input report (KS, Q-Q), verification tests vs Erlang C |
| **Experimenter** | Replications, CRN, sensitivity, staffing search, statistical bounds | M4 | Experiment plan (accuracy requirement fixed first), results with 95% bounds |
| **Integrator** | Parallel runner, checkpoints, live twin, CI on macOS/Windows/Linux | M5 | Green CI run, resume test, reproducibility fingerprints |
| **Reviewer / Governance lead** | Model card, governance pack, ADR index, ethics review (lesson 26), peer-review coordination | M6 | Model card checked against evidence, signed ADR reviews, risk statement |

**Team rules**
- Every decision with lasting consequences gets an ADR, written by the role that owns it and reviewed by another member.
- Pull requests need one approving reviewer who did not write the code. CI must be green, and no test may be skipped without a recorded reason.
- Weekly 15-minute stand-up notes go in `TEAM-LOG.md`: done, next, blocked, and any number that changed.
- Disputes go first to data (run the experiment), then to the ADR process, then to the instructor.
- Contribution statement: each member lists their commits, ADRs and reviews. The instructor may adjust individual marks by ±20% using the statements, the git history and the oral defence.

## Pair-programming protocol for L200 build tasks (weeks 5-7)

The L200 labs ("Build it") add a feature to working code, and a test (`test_build_task.py`) proves it. Pairs work as follows.

1. **Set-up (5 min).** One laptop or a shared editor. Both run `python -m unittest -v` and see the same baseline. Agree the build task's acceptance test before writing any code.
2. **Roles.** The **driver** types. The **navigator** reads the test, checks each line against the concept note, keeps a list of questions and watches for magic numbers and unseeded randomness.
3. **Swap every 25 minutes** (a timer, not a feeling), or after each passing test, whichever comes first.
4. **Predict before you run.** Before each run the navigator writes down the expected number, as in the tryIt habit. A wrong prediction is discussed before any code changes.
5. **Red → green → explain.** The failing test runs first. Make it pass with the smallest change. The driver then explains the change aloud, and the navigator can veto anything that cannot be explained.
6. **Commit together.** Both names go in the commit (`Co-authored-by:`). The message states the number that changed (e.g. "Erlang B 0.268 matches simulation").
7. **Reflection (5 min).** Each partner writes 2-3 sentences in the lab README: one thing learned and one thing the partner did well. Pairs rotate every week.

**Integrity in pairs.** Code is shared within the pair. Problem-set proofs and essays (L500) are individual. AI assistance must be declared, and the course rule applies: code decides, the model may propose or explain, and every model output is checked by code.
