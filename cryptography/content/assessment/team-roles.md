# Team roles (capstone) and the pair-programming protocol (L200 labs)

## Capstone team roles (teams of 4; roles rotate at the midpoint so everyone holds two)
| Role | Owns | Typical artefacts | Hand-off duty |
|---|---|---|---|
| **Crypto architect** | Key hierarchy, algorithm registry and policy, ADRs | ADRs, registry module, agility fitness function | Explains every algorithm choice at the oral defence |
| **Implementation lead** | Service code, the AEAD/AAD layer, sharing (HPKE) | Code, unit tests, failure-lab reproduction | Keeps the build green; reviews every merge |
| **Verification and threat lead** | Threat model, attack-tree tests, Wycheproof and misuse tests, theorem-style budgets (nonce, birthday) | STRIDE table, attack tree, test suite, budget calculations | Writes the "what would break this" test for every ADR |
| **Operations and ethics lead** | Rotation and revocation runbooks, metrics, disclosure policy, privacy and export notes | Runbook, dashboards or metrics list, SECURITY.md, lesson-26 analysis | Runs the rotation drill; owns the disclosure section of the defence |

**Rules.**
- Every role has a backup, and everyone must be able to explain every component; the oral defence checks this.
- Record decisions in ADRs, and tasks and ownership in the issue tracker.
- Hold a weekly 15-minute stand-up with notes.
- Raise conflicts first in the team, then with the instructor. Peer evaluation at the end, scored 1-5 per member with comments, can adjust individual marks by ±10 %.

## Pair-programming protocol for the L200 labs (lessons 7-11)
1. **Roles.** The *driver* types; the *navigator* reviews each line, checks it against the lesson (API names, parameters, expected outputs) and keeps the step list.
2. **Switch every 20-25 minutes** or at every lab step boundary, whichever comes first. Commit before switching, and include both names in the commit message (`Co-authored-by:`).
3. **Predict, then run.** Before running a step, the navigator says the expected output (e.g. "signature 64 bytes, verify OK"). Any mismatch is investigated before moving on.
4. **Security hygiene.** Use demo keys only and never paste real secrets. Use `secrets`/`os.urandom` for anything secret, and use a seeded `random` only for simulations. Run attacks only on localhost (127.0.0.1).
5. **Local agents** (if used): the navigator checks every agent suggestion with code or the lesson before the driver types it (agent-assist rule: code decides, the agent explains).
6. **Disagreements.** Write both options as a test or a two-line experiment and let the output decide. If that does not settle it, ask a TA.
7. **Submission.** Both partners sign the checkpoint statement and write a short individual reflection: one thing learned and one thing the partner explained.
8. **Integrity.** Pairs share code within the pair only. Problem sets and exams remain individual (syllabus).
