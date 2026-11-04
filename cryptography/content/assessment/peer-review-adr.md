# Peer review of Architecture Decision Records (weeks 12-13)

Each student writes **two ADRs** in Nygard format (Context / Decision / Status / Consequences, as in labs/L400/*/ADR-*.md). One is on a lesson 17-21 design decision and one is on a capstone decision. Each ADR gets **two peer reviews**, which are assigned at random. The author revises the ADR and answers every review comment. The grade counts the ADR, the quality of the reviews the student gives, and the response (5 % in total).

## Reviewer checklist (answer every item yes / no / partly, with a comment)
**Context**
- [ ] Is the problem stated with constraints that can be checked (data lifetime, throughput, platforms, compliance)?
- [ ] Are the threats named, ideally linked to a threat model (L400 #21)?

**Options and evidence**
- [ ] Are at least two real alternatives considered, including "do nothing" where it makes sense?
- [ ] Is each option backed by **measured or calculated evidence**: lab output, byte counts, nonce or birthday budget (lesson 24), or a benchmark with its method?
- [ ] Are numbers reproducible (script path, version pins such as cryptography 50.0.2)?

**Decision**
- [ ] Does the decision follow from the evidence, and are its trade-offs explicit?
- [ ] Does the security argument name the property needed (IND-CCA, INT-CTXT, EUF-CMA, forward secrecy) and the assumption it rests on (lesson 25)?
- [ ] Are failure modes covered: silent downgrade, nonce reuse, key loss, revocation lag?

**Consequences and verification**
- [ ] Is there a **fitness function or test** that would fail if the decision were violated?
- [ ] Is there an operational **metric or signal** that shows when the decision stops being valid (e.g. message count per key, envelopes by algorithm)?
- [ ] Are migration and rollback paths described?

**Professional aspects**
- [ ] Are privacy, legal or export implications flagged where relevant (lesson 26)?
- [ ] Are sources cited, with no marketing claims?

## How to write review comments
Be specific and constructive. Point to a line and say what is missing and why it matters, for example: "Section 2 claims random nonces are fine. At 10^4 msg/s the 2^32 budget is reached in about 5 days; please add the rotation period." Separate **must-fix** (correctness or security) from **suggestions**. Do not rewrite the author's decision; ask questions that test it. Follow ACM Code 2.4: give constructive, critical reviews.

## Rubric
| Criterion | Excellent | Adequate | Inadequate | Weight |
|---|---|---|---|---|
| ADR quality (author) | Evidence-based options, explicit trade-offs, fitness function and metric | Decision justified, evidence thin | Opinion only | 40 |
| Review quality (reviewer) | Checklist complete; specific must-fix vs suggestion comments with reasons | Generic but correct comments | "Looks good" or incorrect comments | 35 |
| Response and revision (author) | Every comment answered; changes or reasoned rejections | Most comments answered | Ignored reviews | 25 |
