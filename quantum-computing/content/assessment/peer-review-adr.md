# Peer review of Architecture Decision Records (ADRs)

**When:** two rounds, in week 10 (an L400 #17-#18 lab ADR) and week 13 (capstone ADRs). **How:** each student reviews two ADRs by other teams, assigned at random and anonymised where possible. Each review takes about 45 minutes and runs to 300-500 words, plus the checklist below. The review itself is graded (5% of the course); the reviewed ADR is not graded on the review.

ADRs in this course use Michael Nygard's format (Title, Status, Context, Decision, Consequences), as in `labs/L400/*/docs/adr/`.

## Checklist (tick, then justify every "no" in the review text)

**Structure**
- [ ] Title is a short noun phrase naming the decision. Status is present (proposed, accepted, superseded by ...).
- [ ] Context states the forces: requirements, constraints and budgets, with numbers where they exist.
- [ ] Decision is one clear sentence in the active voice ("We will ...").
- [ ] Consequences list both benefits and costs, including what becomes harder.

**Evidence**
- [ ] At least two options were considered, and the rejected ones are named with a reason.
- [ ] Every number quoted comes from code that ran (a lab script, a test, `run_capstone.py`), and the reviewer reran at least one.
- [ ] The comparison is fair: same budget, seeds and instances for quantum and classical options (L400 #18).
- [ ] Assumptions are explicit (noise model, error rates, problem sizes). Limits of a simulator-only result are stated.

**Keeping it true**
- [ ] A fitness function or test enforces the decision (`test_fitness.py`), and the reviewer ran it.
- [ ] A reversal condition is stated ("revisit if ...").
- [ ] The ADR links to the lessons, theorems or sources it relies on (e.g. T25.1 for Grover iteration counts).

**Honesty and responsibility**
- [ ] No unsupported claims ("quantum is faster", "secure against quantum"). Each claim matches its evidence (ACM 1.3, IEEE 7.8 item 5).
- [ ] Security implications are covered where relevant (crypto in transit and at rest, HNDL for long-lived data, L400 #21).
- [ ] Data handling, access and dependency risks are mentioned where relevant (vendor lock-in, export-controlled hardware, cost to users).

## Writing the review

1. **Summary (2-3 sentences):** restate the decision and its main reason, to show you understood it.
2. **Strengths:** what the authors should keep.
3. **Major issues:** anything that would change the decision, such as missing evidence, an unfair comparison or a broken fitness test. Give a concrete fix for each.
4. **Minor issues:** wording, structure, missing links.
5. **Reproduction note:** the command you ran and what you observed.

Be specific and respectful, and critique the decision, not the people (ACM 2.4: "provide constructive, critical reviews of others' work").

## Rubric for the review (graded)

| Criterion | Excellent | Adequate | Inadequate | Weight |
|---|---|---|---|---|
| Understanding | The summary is accurate and shows why the decision was made. | The summary is accurate but shallow. | The summary misstates the decision. | 15 |
| Verification | Reran code or tests, reports real output, and notes any discrepancy. | Mentions running something without details. | No reproduction attempt. | 25 |
| Quality of critique | Finds the issues that matter most (evidence, fairness, fitness) and ranks them. Every point is actionable. | Valid points, mostly minor or unprioritised. | Generic praise or nitpicks only. | 30 |
| Responsibility lens | Checks claims, security and data/access risks with sources. | Mentions them briefly. | Ignores them. | 15 |
| Professional tone | Specific, respectful and concise, within the length. | Mostly constructive. | Dismissive or personal. | 15 |
