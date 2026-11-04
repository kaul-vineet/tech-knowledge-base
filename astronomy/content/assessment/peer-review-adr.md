# Peer review of Architecture Decision Records (ADRs)

**Context.** L400 lessons 17 and 19 and the capstone (22) ask for ADRs in Nygard form: Title, Status, Context, Decision, Consequences, plus the fitness test that guards the decision. In week 13, every student reviews two ADRs written by others. The review is graded, and so is the author's response to it.
**Weight:** ADRs plus reviews make up 5 % of the course: 3 % for the author's ADRs after revision, 2 % for the quality of the reviews given.

## Reviewer checklist (answer every item yes / no / partly, with one line of evidence)
**Structure**
- [ ] Title states the decision, not the topic ("Use vectorised batches for the survey pipeline", not "Pipeline").
- [ ] Status and date are present; superseded ADRs link to their successor.
- [ ] Context, Decision and Consequences are separate and none is empty.

**Context**
- [ ] The forces are stated with numbers where possible (throughput, latency, data volume, team size).
- [ ] Constraints from outside the code are named: licences, platform (macOS/Windows), funding, ethics.
- [ ] At least two real alternatives are described, including "do nothing".

**Decision and evidence**
- [ ] The decision follows from the context; a reader can see why the alternatives lost.
- [ ] Every quantitative claim is backed by a reproducible measurement (script, seed, best-of-N) and the ADR says where it is.
- [ ] Uncertainty in the measurements is acknowledged (variance between runs, single-CPU sandbox).

**Consequences**
- [ ] Negative consequences are listed honestly (complexity, memory, lock-in, users affected).
- [ ] Consequences for other people are considered where relevant: downstream data users, alert consumers, licence holders.

**Guarding the decision**
- [ ] A fitness function or test exists, runs in CI, and would fail if the decision were silently reverted.
- [ ] The ADR states when to revisit the decision (a trigger: data volume, a new library version, a new regulation).

## Writing the review
- 200–400 words.
- Start with what the ADR does well.
- Then give the three most important issues, each tied to a checklist item, with a concrete suggestion.
- End with a recommendation: accept / accept with minor changes / revise.
- Be specific and respectful. Critique the document, not the author (ACM Code 2.4: "provide constructive, critical reviews of others' work").

## Author's response
For each issue, reply in a short table: issue | accepted / declined | change made or reason. Declining is allowed when it is justified.

## Rubric for the review (reviewer's mark)
| Criterion | Weight | Excellent | Adequate | Inadequate |
|---|---|---|---|---|
| Accuracy | 30 | Every issue raised is real and correctly explained | Mostly real issues; one misreading | Raises non-issues or misreads the ADR |
| Priority | 25 | The three issues are the most important ones | Important issues mixed with cosmetic ones | Only cosmetic issues |
| Actionability | 25 | Each issue has a concrete, feasible suggestion | Suggestions vague | No suggestions |
| Tone and professionalism | 20 | Constructive, specific, respectful | Neutral but terse | Dismissive or personal |

## Rubric for the revised ADR (author's mark)
| Criterion | Weight | Excellent | Adequate | Inadequate |
|---|---|---|---|---|
| Completeness of structure | 20 | All sections, status and date | One section thin | Missing sections |
| Evidence | 30 | Reproducible measurements with variance | Measurements without variance or location | Assertions only |
| Alternatives and consequences | 25 | Real alternatives; honest negatives; people affected | Alternatives shallow | Single option, no negatives |
| Guarding and response to review | 25 | Fitness test in CI; review handled point by point | Test exists; review partly addressed | No test; review ignored |
