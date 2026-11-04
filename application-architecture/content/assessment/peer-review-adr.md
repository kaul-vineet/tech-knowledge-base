# Peer review of Architecture Decision Records (ADRs)

Each student writes or revises two ADRs for the capstone (format: Nygard – Title, Status, Context, Decision, Consequences;
see lesson 6 and `labs/L400/22-capstone/adr/`). Each ADR is reviewed by two classmates from another team (double-blind
where practical). Reviews are graded on their **quality**, not on the grade they give. ADRs plus reviews = 4 % of the course.

## Reviewer checklist
**Context**
- [ ] States the forces: the quality attribute scenario(s) at stake, with measurable response measures (lesson 24).
- [ ] Separates facts (measured, with source) from assumptions (stated as such).
- [ ] Names the stakeholders affected, including users who are not in the room (accessibility, privacy – lesson 26).

**Decision**
- [ ] Says what was decided in one or two sentences, in active voice.
- [ ] Lists at least two options that were considered and why they lost.
- [ ] If the decision depends on a weight or threshold, states it (sensitivity point) and when it would flip (lesson 24, T24.4).

**Consequences**
- [ ] Lists what becomes easier *and* what becomes harder (no consequence section that only lists benefits).
- [ ] Names the fitness function, test or scorecard criterion that keeps the decision true, and where it runs.
- [ ] Records accepted technical debt honestly: what, who pays the interest, owner, repayment date (lesson 26).

**Evidence and integrity**
- [ ] Every number is reproducible from a lab output, script or cited source.
- [ ] Claims about standards or law are cited and not overstated ("conforms to" only with evidence).
- [ ] Use of a local model, if any, is disclosed and its output was checked.

## How to write the review (150–300 words)
1. One-sentence summary of the decision in your own words (proves you understood it).
2. The two strongest points.
3. The two most important weaknesses, each with a concrete suggestion ("add the p99 at 800 libraries from `app.py
   --solution`" rather than "needs more data").
4. One question the author should answer in the oral defence.
Be specific, kind and honest (ACM Code 2.4: accept and provide appropriate professional review).

## Rubric – ADR (author)
| Criterion | Excellent | Adequate | Inadequate | Weight |
|---|---|---|---|---|
| Context | Forces as measurable scenarios; facts vs assumptions | Forces stated, partly measurable | Vague or missing | 25 % |
| Options and decision | ≥ 2 real options, reasons, sensitivity stated | Options listed, thin reasons | Single option asserted | 25 % |
| Consequences | Costs and benefits, debt recorded honestly | Mostly benefits | Benefits only | 20 % |
| Enforcement | Named fitness function/test that runs in CI | Mentioned, not implemented | None | 20 % |
| Revision after review | Responds to each review point (accepted or argued) | Partial response | Ignores reviews | 10 % |

## Rubric – review (reviewer)
| Criterion | Excellent | Adequate | Inadequate | Weight |
|---|---|---|---|---|
| Accuracy | Summary shows full understanding | Minor misreading | Misunderstands the decision | 30 % |
| Specificity | Each weakness has a concrete, actionable fix | Some generic comments | Only generic praise/criticism | 40 % |
| Checklist coverage | Addresses context, decision, consequences, evidence | Misses one area | Misses several | 20 % |
| Tone | Respectful and direct | Mostly | Dismissive or vague | 10 % |
