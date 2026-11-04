# Peer review of Architecture Decision Records (weeks 9–13)

Each team writes ADRs for its L400 decisions (lessons 17–22 each produce a `decisionRecord`). Every student reviews **two ADRs from another team**, using the checklist, within 4 days. Authors reply to each comment (accept / reject with reason) and revise. Reviews are graded, not the review's verdict.

## Checklist (answer every item yes / partly / no, with one sentence)
1. **Context** states the forces: what the system must do, constraints (power, radio, classroom), and who is affected.
2. **Decision** is one sentence in active voice and can be tested.
3. **Options** — at least two real alternatives, including the simplest one, with why each was or was not chosen.
4. **Evidence** — at least one number from the team's own run (a test, scorecard line or model output), with whether it came from the stub, the simulator or hardware.
5. **Theory** — where relevant, the L500 result the decision rests on (e.g. sampling rate vs aliasing; utilisation and blocking; CRC vs MAC) and its assumptions.
6. **Consequences** — positive and negative, including power/battery, privacy (what data leaves the room) and accessibility.
7. **Fitness check** — how the team will notice if the decision stops holding (a test, metric or log field).
8. **Status and date** — proposed / accepted / superseded, with links to superseding ADRs.
9. **Scope** — no secrets, keys or personal data in the ADR.
10. **Clarity** — a newcomer could implement the decision from the ADR.

## Writing the review
- Lead with the most important issue; separate **must fix** from **suggestions**.
- Quote the ADR line you comment on; propose a concrete change.
- Be specific and respectful: comment on the document, not the person.

## Rubric for the reviewer (50 points) and the author's response (50 points); 5 % of the course with the ADRs themselves
| Criterion | Excellent | Adequate | Inadequate | Weight |
|---|---|---|---|---|
| Reviewer: coverage of the checklist | All 10 items answered with reasons | 6–9 items | Fewer than 6 | 15 |
| Reviewer: technical depth | Finds a substantive issue (missing option, wrong number, violated assumption) and proposes a fix | Mostly surface issues | Only style comments | 25 |
| Reviewer: tone and actionability | Prioritised, specific, respectful | Specific but unprioritised | Vague or dismissive | 10 |
| Author: response quality | Every comment answered; accepted changes made; rejections justified with evidence | Most comments answered | Comments ignored | 30 |
| Author: improvement of the ADR | Revised ADR clearly better (evidence, options, consequences) | Minor changes | No change | 20 |
