# Team roles for the capstone, and the pair-programming protocol for L200

## Capstone teams (3–4 students, weeks 11–14)
Roles rotate once, at the start of week 13, so everyone holds two roles. Everyone writes code and every member must be able
to explain all of it in the oral defence; roles add a responsibility, they do not remove one.

| Role | Responsible for | Evidence at the defence |
|---|---|---|
| **Architect / ADR owner** | Keeps the decision log (`adr/`), runs the mini-ATAM (utility tree, risks, trade-off points), chairs design discussions | ADR log, utility tree, list of risks with owners |
| **Quality and fitness owner** | Scorecard criteria, fitness functions, seeded fault drills, CI green; refuses GO without evidence | Scorecard output, `test_faults.py`, CI history |
| **Reliability and capacity owner** | SLOs, burn-rate alerts, availability estimate with assumptions, capacity plan and N + 1 | SLO report, availability calculation, capacity ADR |
| **Responsibility owner** (4th member; otherwise shared by the architect) | Accessibility scenarios (WCAG 2.2 AA), privacy-by-default retention, honest status notes, local-model use disclosure | Accessibility checks and manual test notes, retention fitness function, release note |

**Working agreement (write it in week 11, one page).** Meeting cadence; definition of done (tests, fitness functions,
ADR updated); how decisions are made and recorded; how disagreements escalate (to the instructor after one documented
attempt); how work is split and how contributions are visible (commits, pairing log). Each member submits a short
confidential peer-contribution form in week 14; large, consistent discrepancies are discussed with the team before grades
are adjusted.

## Pair-programming protocol (L200 labs, lessons 7–11)
L200 labs ("build it") are done in pairs; problem sets and exams remain individual.

1. **Roles.** *Driver* types and thinks aloud about the next small step; *navigator* reviews each line, keeps the build
   task and its test in view, and watches for boundary and invariant violations.
2. **Switch every 20–25 minutes** or at every green test, whichever comes first. Use a timer.
3. **Start from the failing test.** Run `test_build_task.py` with `CHECK_MINE=1` first; agree on the smallest change that
   makes one assertion pass.
4. **Navigator questions** (use at least one per switch): Which port does this call? Can any path bypass this rule? What
   happens if this runs twice? What will the reviewer of this diff ask?
5. **Both names on the commit** (e.g. a `Co-authored-by:` trailer) and a three-line pairing log in the lab reflection: who
   drove which part, one disagreement and how it was resolved, one thing learned from the partner.
6. **Remote pairs** share one editor session or screen; the navigator never types in the shared session.
7. **Fairness.** Pairs change after every two labs. If a partner does not show up, work alone and tell the instructor;
   you are not penalised.
8. **Integrity.** Pairs may not share code with other pairs. Using a local model is allowed if disclosed in the log and
   both partners can explain the result.
