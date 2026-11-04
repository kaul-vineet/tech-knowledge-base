# Final exam – Application Architecture (exam week)

**Covers:** L100–L500 (lessons 1–27). **Time:** 2 hours. **Total:** 80 marks.
**Allowed:** one A4 sheet of your own notes and a non-programmable calculator.
Numbers in model answers were computed by code (`research/l500_checks.py`, section "exam numbers").

---

### Q1 (derivation + calculation, 12 marks)
Library Loans runs behind a load balancer (99.99 %) with three API replicas (99.9 % each, at least one needed) and a
database (99.95 %). (a) Derive the parallel formula and compute the availability of the request path, assuming independent
failures. (b) All replicas read a shared configuration service (99.95 %) and fail without it. Recompute the availability
and the expected downtime per 30-day window. (c) Which assumption of (a) did (b) break, and what does that teach about
"adding replicas"?

**Model answer.** (a) Replicas are all down with probability ∏(1 − Aᵢ), so A_par = 1 − 0.001³ ≈ 1 (3). Path:
0.9999 × (1 − 10⁻⁹) × 0.9995 = 99.9400% (2). (b) Multiply by 0.9995: 99.8900%; downtime (1 − A) × 43,200 min = 47.5 min
per 30 days (4). (c) Independence: the shared configuration service is a common cause, a series element that no number of
replicas can mask; availability is bounded by the critical dependencies (T24.1 upper bound) (3).

### Q2 (calculation + explanation, 10 marks)
The availability SLO of POST /loans is 99.9 % over 30 days. In the last hour 0.5 % of requests failed. (a) Compute the
burn rate. (b) What share of the 30-day error budget did that hour consume? (c) Would the multiwindow page alert from
lesson 15 (1 h / 5 min windows, burn rate ≥ 14.4) fire? Explain why a burn-rate alert is better than "error rate > 0.1 %".

**Model answer.** (a) burn = bad ratio / (1 − SLO) = 0.005 / 0.001 = 5.0 (3). (b) 5 × 1 h / 720 h = 0.69% of the budget
(3). (c) No, 5 < 14.4 – at this rate the budget would last 6 days, which is a ticket, not a page (2). Burn rate scales the
alert to how fast the budget is being spent; a fixed threshold pages on brief blips and misses slow, long burns (2).

### Q3 (calculation, 8 marks)
After growth to 800 libraries the peak is 240 req/s; one instance handles 75 req/s within the p99 SLO; mean service time
is 45.2 ms. (a) Use Little's law for requests in flight at peak. (b) Size with 80 % headroom and N + 1.

**Model answer.** (a) L = λW = 240 × 0.0452 ≈ 10.8 requests in flight (3). (b) ⌈240 / (75 × 0.8)⌉ + 1 = 4 + 1 = 5
instances (5). Sizing on the average or at 100 % utilisation leaves no spare for a crash or deploy (lesson 21).

### Q4 (proof, 10 marks)
(a) State the invariant of the `Member` aggregate and the premises under which it holds in every reachable state; prove it
by induction. (b) A colleague proposes `PremiumMember(Member)` whose `borrow` raises for members with overdue loans,
"because premium is stricter". Is it a behavioural subtype? Justify with the Liskov rule.

**Model answer.** (a) Inv: at most `max_loans` active loans and no book twice among them. Premises: Inv after construction;
each public operation preserves Inv when its precondition holds; rejected calls change nothing; no other way to change
state (encapsulation) (3). Induction on the number of calls: base by construction; step – a rejected call leaves the state
unchanged, an accepted one preserves Inv (3). (b) No: it strengthens the precondition – it refuses calls the supertype
accepts – so a client correct for `Member` can fail; substitutes may only weaken preconditions and strengthen
postconditions (T25.2). Model it as a policy object or a separate type instead (4).

### Q5 (prediction, 8 marks)
The buggy check-then-act borrow workflow (read "book free", later insert a loan) is model-checked with **three** members
instead of two. (a) Predict the length of the shortest counterexample BFS returns and justify. (b) What is the reachable
state count of the buggy model, and why does it matter for model checking?

**Model answer.** (a) 4 steps – two members read "free" and both insert; a third member is not needed, and BFS returns a
shortest trace (T25.3) (4). (b) 3³ = 27 states: each member is idle, checked or holding; the count grows as 3ⁿ, so
exhaustive search explodes with more members (state explosion); bound the model and use reductions (4).

### Q6 (design critique, 12 marks)
An ADR for Library Loans reads: "Decision: move fines into a separate service now (big bang), shared schema for all
tenants, tenant filtering in the UI. Consequences: faster delivery." Critique it using lessons 17, 18, 20 and 23, and
rewrite the Decision and Consequences sections.

**Model answer.** Big bang: no parallel run or measured cut-over criterion (lesson 17 found 108 mismatches out of 2,000
shadow requests from a rounding bug) (3). Tenant filtering in the UI: data-layer queries can leak across tenants
(lesson 18's report leaked 686 of 700 rows); the guard belongs in every query, checked by a fitness function (3). No
expand/contract plan for the schema change (lesson 20) and no statement of what becomes harder (3). Rewrite: "Extract fines
behind a facade, shadow 2,000 requests, cut over at ≤ 0.1 % mismatches with 0 errors; tenant-scoped queries enforced by
TenantGuard and a CI check; schema change by expand/contract. Consequences: two code paths during migration; extra CI
gates; rollback by flag." (3)

### Q7 (short explanation, 10 marks)
(a) Name two WCAG 2.2 AA success criteria that depend on architectural choices and say which choice. (b) What does GDPR
Article 25(2) require by default, and how would you implement it for loan history? (c) A manager wants to tell a funder the
service is "fully compliant" although known AA failures remain. What do you say, citing the ACM Code?

**Model answer.** (a) 3.3.8 Accessible Authentication (Minimum) – choice of identity provider/sign-in method; 2.5.7
Dragging Movements – choice of component library (or 2.5.8 Target Size) (3). (b) By default only personal data necessary
for each purpose are processed, including storage period and accessibility; implement deletion/anonymisation of returned
loans after a fixed period, opt-in history, pseudonymised analytics, enforced by a retention fitness function (4). (c) The
claim is false; ACM 1.3 requires honesty and full disclosure of limitations, and 1.4 notes that failing to design for
accessibility may be discrimination. Offer a true statement: gaps, mitigation, owner, date (3).

### Q8 (calculation + evaluation, 10 marks)
Two options are scored on (availability, simplicity): A = (0.6, 0.8), B = (0.9, 0.4), with weights (w, 1 − w).
(a) Compute the break-even weight w*. (b) Which option wins at w = 0.5, with what scores? (c) Relate w* to ATAM's
sensitivity and trade-off points and say what you would record in the ADR.

**Model answer.** (a) d = A − B = (−0.3, 0.4); w* = d₂ / (d₂ − d₁) = 0.4 / 0.7 = 0.571 (4). (b) A: 0.5·0.6 + 0.5·0.8 = 0.70;
B: 0.5·0.9 + 0.5·0.4 = 0.65 – A wins (3). (c) The weight is a sensitivity point of the decision; the option choice is a
trade-off point because it moves availability and simplicity in opposite directions. Record the weight, who set it, w*, and
the evidence that would change the decision (3).
