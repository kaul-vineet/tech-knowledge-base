# Peer review of Architecture Decision Records (weeks 6 and 12)

Each student reviews two ADRs written by another team (lesson 11's design note in week 6; one L400 or capstone ADR in week 12). ADRs follow the Nygard format used in `labs/L400/*/ADR-*.md`: Title, Status, Context, Decision, Consequences. Reviews are signed, shared with the authors, and graded (part of the 5% "ADRs and peer reviews").

## Checklist (answer every item yes / no / partly, with one sentence of evidence)
**Context**
- [ ] The problem and its constraints are stated as numbers (latency budget, RPO/RTO, stale-read share, availability target).
- [ ] The system model is explicit: fault types (crash, partition, Byzantine?), timing assumptions, what is out of scope.
- [ ] Stakeholders and who is harmed if the decision is wrong are named (lesson 26).

**Options**
- [ ] At least two real alternatives are compared, including "do nothing" where sensible.
- [ ] Each option has measured evidence from a seeded lab run (command + output), not only opinion.
- [ ] Costs are complete: latency, availability under failure, operational load, money, energy, data residency.

**Decision**
- [ ] The decision follows from the evidence; the deciding measurement is identified.
- [ ] Claims are correct with respect to theory (e.g. no "CAP lets us have all three when healthy, so we are CA"; quorum sizes satisfy R + W > N where overlap is claimed; no safety that depends on a timeout).
- [ ] Limits are stated honestly (what the design does not guarantee).

**Consequences and verification**
- [ ] A fitness function or test keeps the decision true (`test_fitness.py`), and it fails on the rejected option.
- [ ] Scaling limits and the trigger for revisiting the ADR are given.
- [ ] Status and date are set; superseded ADRs are linked.

## Review rubric (per review, 10 points)
| Criterion | Excellent | Adequate | Inadequate | Weight |
|---|---|---|---|---|
| Accuracy | Every checklist answer is correct and backed by a quote or line reference | Mostly correct; some unsupported answers | Checklist ticked without reading | 40% |
| Depth | Finds at least one substantive issue (missing option, wrong theory claim, untested consequence) and explains its impact | Finds surface issues only | No issues found where some exist | 30% |
| Constructiveness | Each issue has a concrete, feasible suggestion; tone is professional and blameless | Suggestions vague | Dismissive or personal | 20% |
| Brevity | 300-500 words, prioritised | Over length but organised | Unstructured | 10% |

Authors respond in writing to every point (accept, reject with reason, or defer with an issue link); the response is part of their ADR mark.
