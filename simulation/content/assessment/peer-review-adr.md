# Peer review of Architecture Decision Records (ADRs)

ADRs in this course follow Nygard's format: Title, Status, Context, Decision, Consequences. Examples are in every `labs/L400/*/decisions/` folder. Each student writes two ADRs (week 11 from an L400 lab, week 13 from the capstone) and reviews two peers' ADRs in each round. Reviews are signed and returned within 5 days, and the author replies to each point. Together, the ADRs and the reviews are worth 4% of the course (ADR quality 2.5%, review quality 1.5%).

## Reviewer checklist (answer each with Yes / Partly / No plus one sentence of evidence)

**Context**
1. Is the problem stated with the measured numbers that motivated it (not "performance was bad")?
2. Are the options listed and compared on the *same* budget and inputs, e.g. same runs and common random numbers (L400 #18)?
3. Is the evidence reproducible: a named script, a seed, a commit or a file hash?
4. Are the assumptions and the validity envelope stated (Sargent: domain of applicability)?

**Decision**
5. Is the decision a single, testable statement ("use X with parameter Y"), not a preference?
6. Was the decision criterion, such as the accuracy requirement or SLA, fixed *before* the comparison?
7. Does it follow from the evidence, so that another reader would make the same choice?

**Consequences**
8. Are the downsides and scaling limits stated, with a number where possible?
9. Is there a fitness function or test that fails if the decision stops being true?
10. Is there a revisit trigger (a threshold, a date or an event)?

**Responsibility**
11. Are the people affected by the decision, and any risk to them, considered (lesson 26)?
12. Is the role of any AI assistance stated, with the rule that code decides and the model explains?

## Rubric for the ADR (author)

| Criterion | Excellent | Adequate | Inadequate | Weight |
|---|---|---|---|---|
| Evidence-based context | Options measured fairly, numbers reproducible | Some numbers, unclear fairness | Opinion only | 30 |
| Decision clarity | One testable decision with criteria fixed in advance | Clear but criteria implicit | Vague or several decisions | 20 |
| Consequences and limits | Downsides, scaling limits, envelope and revisit trigger | Some consequences | None or only benefits | 25 |
| Fitness function | Automated test that guards the decision and fails on regression | Manual check described | None | 15 |
| Responsibility | Affected people and AI use addressed | Mentioned | Absent | 10 |

## Rubric for the review (reviewer)

| Criterion | Excellent | Adequate | Inadequate | Weight |
|---|---|---|---|---|
| Accuracy | Every checklist item answered with specific evidence | Most items answered | Generic praise or criticism | 40 |
| Actionability | Concrete, prioritised suggestions that can be tested | Some concrete suggestions | None | 35 |
| Professional tone | Respectful, about the work not the person (ACM 2.4: accept and provide appropriate professional review) | Mostly respectful | Dismissive | 25 |
