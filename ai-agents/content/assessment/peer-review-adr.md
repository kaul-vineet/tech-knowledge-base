# Peer review of Architecture Decision Records (ADRs)

Each team writes three ADRs during the L400 weeks (Nygard format, as in `labs/L400/*/ADR-*.md` and `labs/L400/22-capstone/adr/`). Every ADR is reviewed by two students from another team before it is accepted. Reviewers submit the checklist and a short written review (300–500 words); authors reply and revise. Both the ADR (author) and the review (reviewer) are marked.

## Reviewer checklist

**Structure**
- [ ] Title states the decision, not the topic ("Code decides severity; model proposes" – not "Severity").
- [ ] Status, date and deciders are present; superseded ADRs are linked.
- [ ] Context, Decision, Consequences (and Options considered) are all present.

**Context and options**
- [ ] The problem and its constraints are measurable (numbers, not adjectives).
- [ ] At least two real options are described fairly, including "do nothing" where relevant.
- [ ] Each option has evidence: a measurement from the lab, a cited source, or a calculation – with how it was obtained.

**Reasoning**
- [ ] Rates are reported with n and an interval; comparisons between options on the same cases are paired (lesson 24).
- [ ] Trade-offs with uncertainty are argued with expected cost/utility, and the threshold at which the decision would flip is stated (lesson 25).
- [ ] Budgets, limits and allow-lists are justified, not just listed (lesson 25 T1, T4).
- [ ] Safety, privacy and accountability implications are addressed where relevant (lesson 26), with primary references.

**Consequences and verification**
- [ ] Negative consequences and residual risks are stated honestly.
- [ ] A fitness function or test keeps the decision true, with its threshold, and it runs in CI.
- [ ] The conditions for revisiting the decision are named (e.g. "if the golden set grows past 200", "if the model is upgraded").

**Writing**
- [ ] A new team member could implement and verify the decision from the ADR alone.
- [ ] Sources are cited; no copied text.

## Writing the review
Start with one sentence summarising the decision as you understand it (if you cannot, say so – that is the most useful feedback). Then give: the strongest part; the most important gap, with a concrete fix; any factual or numerical error you reproduced or failed to reproduce (show your command); and a recommendation – accept, accept with changes, or revise and resubmit. Be specific and respectful; review the decision, not the people (ACM Code 2.4: "provide constructive, critical reviews of others' work").

## Rubric for the ADR (author, per ADR)

| Criterion | Excellent | Adequate | Inadequate | Weight |
|---|---|---|---|---|
| Problem and constraints | Measurable constraints tied to the lab or capstone | Constraints stated loosely | Vague or missing | 15 |
| Options and evidence | ≥ 2 options with reproducible evidence | Options listed, evidence thin | One option, no evidence | 25 |
| Reasoning quality | Quantitative (intervals, expected utility, thresholds); assumptions stated | Qualitative but sound | Assertion only | 25 |
| Consequences and verification | Honest consequences; fitness test in CI with threshold | Consequences listed; test not automated | Missing | 20 |
| Response to review | Every point answered; revisions traceable | Most points answered | Ignored | 15 |

## Rubric for the review (reviewer)

| Criterion | Excellent | Adequate | Inadequate | Weight |
|---|---|---|---|---|
| Accuracy | Restates the decision correctly; checks at least one number by re-running | Restates correctly; no re-check | Misreads the ADR | 30 |
| Depth | Finds the most important weakness and proposes a concrete fix | Finds minor issues only | Only formatting comments | 40 |
| Constructiveness and tone | Specific, prioritised, respectful | Mostly specific | Vague or dismissive | 20 |
| Checklist completed | All items with justification | Ticked without notes | Missing | 10 |
