# Capstone oral defence (week 14)

**Format:** 20 minutes per team: 5-minute demonstration of the incident-triage agent (L400 #22) against the fake server, then 15 minutes of questions. Every member answers at least two questions, including one outside their own role. Examiners pick 4–6 questions from the bank below, adapted to the team's ADRs, and may ask the team to run a command live (a test, `eval_capstone.py`, an L500 check). **Weight:** 6 % of the course mark (the capstone system itself is 10 %).

## Question bank

1. **Boundary.** Walk us through what happens when the model proposes `restart_service` for an incident your policy classifies as low severity. Which file decides, and which test proves the model cannot change the outcome? *(Look for: policy.py decides, model only proposes; fitness/fuzz test; approval for side effects.)*
2. **Undecidability.** A reviewer suggests replacing your tool allow-list with a model that inspects each proposed action for danger. Argue for or against using lesson 25 T4. *(Halting reduction; allow-list decides a syntactic, decidable property; model checker as advisory only.)*
3. **Budgets.** Justify your step and retry budgets numerically. What happens to cost if a tool starts failing every time? *(T1: retry while p_i·C_fail ≥ c; correlated failures; p = 0 → cost bounded by k·c.)*
4. **Evaluation power.** Your scorecard says 19/20 golden incidents pass. What is the 95 % interval, and which size of regression would your gate miss? *(Wilson ≈ [0.76, 0.99]; exact power of n = 20 is low for 5–10 point drops; per-case regression rule.)*
5. **Version comparison.** You changed the runbook retrieval. How did you show the new version is not worse, and why is that test appropriate? *(Paired McNemar on the same incidents; discordant cases read by hand; intervals.)*
6. **Act or escalate.** Show the expected-utility or MDP argument behind the threshold at which the agent escalates to a human. What measured quantity would flip the decision, and how do you monitor it? *(Break-even error rate; Wilson upper bound vs threshold; monitoring in production.)*
7. **Exactly-once.** Kill the workflow between "decide" and "act". What prevents a duplicate action on restart? Show the test. *(Event history, idempotency key, outbox; crash-sweep test.)*
8. **Decoding.** Which temperature and sampling settings does your agent use for triage proposals and for summaries, and why? What would change if you used greedy decoding everywhere? *(T1/T4; argmax for structured output validated by schema; sampling for prose; loop risk with greedy.)*
9. **Accountability and transparency.** A customer is harmed by an action your agent took. Who is accountable, what evidence can you produce, and what did you tell users about the agent? *(Deployer accountability – Moffatt; audit log/traces; AI Act Art. 50(1) disclosure; ACM 1.3/2.5.)*
10. **Privacy and oversight.** Which personal data enters prompts and traces, how long is it kept, and how do you stop on-call staff from rubber-stamping the agent's proposals? *(Minimisation, redaction, retention job – ACM 1.6, GDPR Art. 22 where applicable; automation bias – AI Act Art. 14(4)(b), seeded errors, catch-rate metric.)*

## Rubric (per student; the team mark is the mean, moderated by the contribution statement)

| Criterion | Excellent (4) | Good (3) | Adequate (2) | Inadequate (0–1) | Weight |
|---|---|---|---|---|---|
| Technical correctness | Precise answers that match the code and tests; can run a check live | Correct with minor gaps | Partly correct, needs prompting | Incorrect or cannot explain own system | 30 |
| Theoretical grounding | Uses L500 results quantitatively (intervals, power, expected utility, contraction, undecidability) | Uses the right result qualitatively | Mentions theory without applying it | No grounding | 25 |
| Evidence | Points to specific tests, ADRs, traces, scorecard numbers | Mostly specific | General claims | No evidence | 15 |
| Ethics and responsibility | Identifies stakeholders, obligations with primary sources, residual risk | Identifies main obligations | Generic statements | Not addressed | 15 |
| Communication and teamwork | Clear, concise; answers outside own role; builds on teammates | Clear within own role | Hesitant or unclear | Cannot answer | 15 |

Scores are converted as (weighted sum / 4) to a percentage. A student who cannot explain code they submitted is referred under the integrity policy (`syllabus.md`).
