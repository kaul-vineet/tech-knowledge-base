# Team roles for the capstone, and the pair-programming protocol for L200

## Capstone team (3–4 students, lesson 22)
Roles rotate at the two milestone reviews, so that everyone holds at least two roles. Every member must be able to defend the whole system in the oral defence (`capstone-oral-defence.md`).

| Role | Owns | Hand-off artefact |
|---|---|---|
| **Science lead** | The physics and statistics: transit model, duration bound, detection threshold, injection/recovery design | A one-page note of assumptions and the derivations used (links to L23–L25) |
| **Pipeline engineer** | Code structure, performance, determinism, cross-platform behaviour (macOS/Windows) | Passing tests and fitness functions in CI; a reproducibility script |
| **Verification lead** | Tests, injected-signal campaigns, coverage of error bars, the scorecard | Scorecard with the exact commands and seeds; a list of known failure modes |
| **Data & ethics steward** (or shared in teams of 3) | Data sources, licences and acknowledgements, citation (CITATION.cff), public-facing text, local-agent boundary | Release checklist (L21 gate), credits, a "limits of this result" paragraph |

**Rules.**
- Decisions that cross roles are recorded as ADRs, and each ADR is reviewed by a member who did not write it.
- Each member keeps a short log (date, what, commit) used for individual marks.
- If a member is absent for a milestone, the team records it; marks are adjusted on evidence from the logs and commits, not on claims.
- Disagreements go to an ADR with the alternatives. If they are not resolved within a week, the instructor decides.

## Pair programming protocol for L200 (lessons 7–11)
Pairs are assigned for weeks 4–6 and change each week, so that students meet different working styles.

1. **Roles.** The *driver* types; the *navigator* reviews each line, keeps the test list, and watches for the lesson's failure modes. Swap every 25 minutes (a timer, not a feeling).
2. **Start.** Read the lab README together. Write the test you expect to fail first: the build task's `test_build_task.py` with `BUILD_TARGET=mine`.
3. **During.** The navigator says *what* and *why*; the driver decides *how*. Hard parts are explained out loud. If both are stuck for 10 minutes, write down the question and ask, and record it in the README "Questions" section.
4. **Commits.** Small commits with both names (`Co-authored-by:` trailer). Run the tests before every commit.
5. **Finish.** Both partners can explain every function. Each writes a 3-sentence individual reflection: what I learned, what my partner taught me, and what I would do differently.
6. **Fairness.** Either partner may ask the instructor for a private check-in. Persistent imbalance (one partner always driving or absent) is handled by re-pairing, not by penalising the pair.
7. **Remote pairs.** Use a shared editor or screen share with the same 25-minute swaps. Macs and Windows PCs are both fine: the labs are cross-platform (PLATFORM-AGENT-SPEC).

**Assessment link.** L200 labs are marked per pair (same mark), with up to ±10 % individual adjustment from the reflections and the commit history (syllabus: Labs 35 %).
