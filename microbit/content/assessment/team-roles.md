# Team roles (capstone) and the pair-programming protocol (L200)

## Capstone team roles (teams of 4; with 3, merge Reliability and Data steward)
Every member writes code and tests; roles add an owned responsibility, rotate the demo, and decide who answers which oral-defence question.
| Role | Owns | Evidence at the defence |
|---|---|---|
| **Firmware lead** | Board code: sensing, sampling rate, Deep Sleep, task periods and budgets | Task table with U, the RM bound and the blocking term (lesson 25); power estimate (lesson 14) |
| **Network & security lead** | Radio frames, ARQ, CRC + MAC, gateway verification | Forged-frame and lost-ack tests; why CRC and MAC (lessons 12, 19, 25) |
| **Reliability lead** | Fitness functions, fault injection, the digital twin, scorecard | One fault shown failing then passing (lessons 20, 22) |
| **Data steward & accessibility lead** | Data inventory, minimisation, retention, dashboard accessibility, battery/e-waste plan | Field-by-field justification; WCAG 2.2 check of the dashboard; cells per year (lesson 26) |

**Shared duties:** each member authors at least one ADR and reviews two from another team (`peer-review-adr.md`). The team keeps a decision log and a short weekly stand-up note (done / next / blocked).
**Conflict and contribution:** contributions are visible in commits and the decision log. If a member is not contributing, the team raises it with the instructor by week 12; marks can be moderated individually after the oral defence.

## Pair-programming protocol (L200 labs 7–11)
1. **Roles.** The *driver* types; the *navigator* reads the lab brief, checks the expected output and thinks one step ahead. The navigator does not take the keyboard.
2. **Swap** every 20 minutes or at each lab step, whichever comes first (use a timer). Both partners must drive in every lab.
3. **Start** by reading the lab README together and predicting the output of the first test; write the prediction down.
4. **Red–green.** Run the test before changing code; change one thing; run again. Paste the real output into your notes.
5. **Talk aloud.** The driver explains each line as it is written; the navigator asks "how will we know it worked?".
6. **Stuck for 10 minutes?** Re-read the troubleshooting table, then ask another pair, then the instructor.
7. **Submit together** with both names and a two-line reflection each: one thing the partner taught you, one failure you diagnosed.
8. **Integrity.** Pairs share code within the pair only. Problem sets (L500) are individual.

Radio labs (lesson 7) need two boards: in the stub both run in one process; with hardware, each partner owns one board and the pair agrees a radio group to avoid crosstalk with neighbours.
