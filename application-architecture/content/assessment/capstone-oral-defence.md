# Capstone oral defence (lesson 22) – question bank and rubric

**Format.** 20 minutes per team: 5 minutes demo (`python run_capstone.py` → GO, then one seeded `--fault` → NO-GO),
15 minutes questions. Each member answers at least two questions alone. Examiners pick 4–5 questions from the bank below
and follow up with "show me in the code / the ADR / the scorecard output". Adjustments (written format, extra time) are
available on request without penalty.

## Question bank (10)
1. **Scorecard.** Walk us through one criterion of your scorecard from measurement to GO/NO-GO. What would make it pass
   while the system is actually broken (a false GO)? *Looks for:* measure, threshold, evidence in output; an honest weak spot.
2. **Seeded faults.** Pick one fault (`fines-rounding`, `cross-tenant-policy`, `unscoped-query`, `duplicate-delivery`).
   Which check catches it, and what fault of the same class would it miss?
3. **Boundaries (L500 #23).** Draw the dependency graph of your capstone modules. Is it strictly layered? Where are the
   cycles or strongly connected components, if any, and how does a fitness function keep it that way?
4. **Information hiding.** Which design decision is hidden behind the fines facade, and what would leak if the legacy
   module were imported directly?
5. **Availability (L500 #24).** Estimate the availability of the borrow path from your components, stating the
   independence assumption. Which single dependency bounds it, and what mitigation did you choose?
6. **Trade-off.** Name one trade-off point in your design (for example tenancy layout, sync vs async e-mail). What weight
   or assumption would flip your decision, and where is it recorded?
7. **Invariants (L500 #25).** State an invariant your system must never break and explain why it holds on *every* path,
   including retries and duplicate events. Where could encapsulation be bypassed?
8. **Contracts.** A consumer adds a new field it expects. Walk through what your contract tests do before and after the
   provider changes. What does a passing contract test *not* guarantee?
9. **Local model.** Your release note is drafted by a local model. Show how code verifies it and what happens when the
   model invents a number. Why must the model never decide GO/NO-GO?
10. **Responsibility (L500 #26).** Your launch is two days away and the borrow flow fails WCAG 2.2 AA 3.3.8. What do you
    tell the stakeholders, and what do you change in the scorecard so this is caught next time?

## Rubric (per student; 6 % of the course grade)
| Criterion | Excellent (4) | Adequate (2–3) | Inadequate (0–1) | Weight |
|---|---|---|---|---|
| Technical correctness | Answers are correct, precise and tied to code/output | Mostly correct, some vagueness | Incorrect or contradicts the code | 30 % |
| Evidence | Points to the exact test, metric, ADR or scorecard line | Refers to evidence generally | Asserts without evidence | 20 % |
| Reasoning about trade-offs and limits | Names assumptions, failure cases and what would change the decision | Names a trade-off without limits | Presents choices as obviously right | 20 % |
| Theory link (L500) | Uses layering/acyclicity, availability maths or invariant reasoning correctly | Mentions theory loosely | No link or misused | 15 % |
| Communication and ownership | Clear, concise; owns mistakes; answers own questions | Understandable with prompting | Relies on teammates; cannot explain own code | 15 % |

Score = Σ (level/4 × weight). A student who cannot explain code they submitted is referred under the integrity policy.
