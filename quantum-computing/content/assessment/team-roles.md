# Team roles (capstone) and pair-programming protocol (L200)

## Capstone team (4 students; teams of 3 merge roles 3 and 4)

Each role owns a part of the L400 #22 service and its evidence. Everyone writes code and tests, and everyone must be able to explain the whole service in the oral defence.

| Role | Owns | Primary artefacts | Lessons |
|---|---|---|---|
| 1. Architect / ADR lead | The decision record and the interfaces between components. Chairs the decision meetings. | `docs/adr/0001-0004`, `architecture.mmd`, interface docstrings | L400 #17, #22 |
| 2. Quantum lead | The QAOA path: circuits, compilation, noise model and readout mitigation. | `noisy_backend.py`, compilation settings, mitigation code and tests | L300 #12-#14, L400 #20 |
| 3. Baseline and benchmark lead | Classical solvers and the fair benchmark harness: budgets, seeds and `decide()`. | Benchmark config, solver code, `test_fitness.py` for fairness | L400 #18 |
| 4. Reliability and responsibility lead | Feasibility gate, orchestration, retries, CI, agent-assist guardrails, and the security/ethics review of claims and crypto. | Feasibility table, orchestrator tests, CI workflow, claims checklist | L400 #19, #21, L500 #26 |

**Rotations and shared duties**
- Each week a different member is **scribe**: meeting notes, decisions and action items, kept in `docs/meetings/`.
- Each week a different member is **reviewer of record**: no merge without their approval and a green test run.
- Every ADR needs approval from someone other than its author, and the peer-review checklist (`peer-review-adr.md`) is applied before acceptance.
- Contributions are visible in commits. Use `Co-authored-by:` trailers for pair work.

**Team charter (agree in week 12, one page):** meeting times, how decisions are made (consensus, then majority), response time for reviews, what happens if someone misses a deadline, and how the team will raise and resolve conflicts. Escalate to the instructor after one documented attempt to resolve an issue inside the team.

**Peer assessment:** at the end of the capstone, each member rates each teammate (including themself) on contribution, reliability and collaboration, from 1 to 5, with one sentence each. Ratings can move an individual's capstone mark by up to ±10% of the team mark. A large disagreement triggers a short meeting with the instructor.

## Pair-programming protocol (L200 labs #7-#11)

L200 labs are done in pairs, with both names on the submission.

1. **Roles.** The *driver* types; the *navigator* reads the lab README, predicts the output before each run, and checks the code against the theory (e.g. T25.1 for Grover iteration counts, T23.2 for bit order).
2. **Swap every 25 minutes**, or at each green test run, whichever comes first. Use a timer. Swap even in mid-thought, and the navigator states the plan aloud before taking the keyboard.
3. **Predict, run, compare.** Before running any script or `try_it.py`, the navigator writes the predicted result in the shared notes. Afterwards, the pair records the observed output and explains any difference.
4. **Tests gate the swap.** Run `python -m unittest -v` before swapping, and do not hand over a red build without saying why it is red.
5. **Build task.** For the `solution_*` / `test_build_task.py` step, the person who did *not* drive the main lab drives the build task.
6. **Remote pairing:** share the screen or use a collaborative editor, with the same timer. Cameras are optional, voices on.
7. **Record.** Commit with both names (`Co-authored-by:`). Add a three-line reflection to the README: one thing each partner taught the other, and one open question.
8. **Fairness.** If one partner consistently drives or navigates, the instructor may ask each to explain the lab individually. Partners rotate after two labs, so nobody pairs with the same person for all of L200.
