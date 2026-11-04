# Team roles for the capstone, and the pair-programming protocol for L200

## Capstone teams (3-4 students, weeks 12-14)
Roles rotate once, at the end of week 13, so everyone holds two roles. Every member writes code and can explain every milestone (the oral defence samples individuals).

| Role | Owns | Evidence at the defence |
|---|---|---|
| **Tech lead / integrator** | architecture.mmd, the run_capstone.py scorecard, merge order, CI green on all three OSes | the integration plan and the CI history |
| **Reliability engineer** | chaos_campaign.py experiments: hypotheses, blast radius, abort conditions; the blameless post-mortem of the worst failure found | experiment log + post-mortem |
| **Correctness lead** | invariants and checks: idempotent consumers, saga log recovery, Raft config safety; linearizability / model-checking runs | the invariants list and which test enforces each |
| **Decision scribe** (4th member; else shared) | ADRs (adr/ADR-022-*), peer-review responses, the limitations section of the README | ADRs with deciding measurements |

Working agreements: a short written plan per milestone (M1-M6), a daily async update (done / next / blocked), decisions recorded as ADRs within 24 hours, and a contribution log (commits plus pairing sessions) submitted with the capstone. Conflicts go to the instructor after one documented attempt to resolve them within the team.

## Pair programming protocol for L200 (#7-#11 build tasks)
L200 build tasks may be done in pairs. The aim is shared understanding, not speed.

1. **Roles.** *Driver* types and narrates; *navigator* reads the test (`test_build_task.py`), the lesson and the concept note, thinks one step ahead and watches for edge cases.
2. **Swap every 20-25 minutes** or at every green test, whichever is first. Use a timer.
3. **Start from a failing test.** Run `BUILD_TARGET=mine python -m unittest test_build_task -v` (Windows: `$env:BUILD_TARGET="mine"`) and read the failure aloud together before writing code.
4. **Say the invariant before the code.** For example: "a fencing token never decreases", "an acked message is never redelivered", "only keys in the moved range change owner". Write it as a comment or an assertion.
5. **One keyboard, one branch.** Commit at every green with both names (`Co-authored-by:` trailer).
6. **Remote pairs** share a screen and the terminal; the navigator keeps the lab README open.
7. **Retrospective (5 minutes).** What did each partner learn? What would you test next? Add two sentences to the lab README's observations section.
8. **Integrity.** Both partners must be able to explain every line. Pairs do not share code with other pairs. Problem sets (#23-#27) stay individual.
