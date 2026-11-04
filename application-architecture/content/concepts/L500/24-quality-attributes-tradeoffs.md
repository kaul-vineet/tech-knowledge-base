**Concept: Quality attributes and trade-off analysis – ISO/IEC 25010:2023, scenarios, utility trees, ATAM and availability maths**

## Why it matters
Functional requirements say what Library Loans does; quality attributes say how well – how available, how fast, how easy to
change, how usable by everyone. They drive the architecture, and they conflict. This lesson gives you three tools: a shared
vocabulary (ISO/IEC 25010), a way to make each "-ility" testable and ranked (scenarios in an ATAM utility tree), and the
probability behind the most quoted number in operations, availability.

## Definitions
- **ISO/IEC 25010:2023 product quality model.** The current edition (edition 2, published 2023-11) defines nine
  characteristics: functional suitability, performance efficiency, compatibility, interaction capability, reliability,
  security, maintainability, flexibility and safety. Compared with the 2011 edition, safety is new, usability became
  *interaction capability* and portability became *flexibility*; inclusivity and self-descriptiveness (interaction
  capability), resistance (security) and scalability (flexibility) were added; maturity became *faultlessness*; and
  accessibility was split into inclusivity and user assistance. (The standard is paywalled; these changes are listed in
  its public foreword.)
- **Quality attribute scenario.** Source, stimulus, environment, artefact, response and response measure. "The system shall
  be highly available" is not testable; "the primary database fails at peak and service is restored within 5 minutes with
  no committed loan lost" is.
- **Utility tree (ATAM).** Root "utility" → quality attributes → refinements → leaf scenarios, each ranked on two axes,
  importance to the business and difficulty for the architecture, using H/M/L because the SEI authors found stakeholders
  cannot reliably make finer distinctions.
- **Risk, non-risk, sensitivity point, trade-off point (ATAM).** A risk is an important decision not yet made or whose
  consequences are not understood; a non-risk is a good decision resting on stated assumptions; a sensitivity point is a
  property a quality response depends on strongly; a trade-off point is a sensitivity point for several qualities that it
  moves in different directions.
- **Availability.** The fraction of time (or of valid requests) the service works. Nines = −log₁₀(1 − A).

## Key results (proofs in `content/L500.json`, checks in `labs/L500/24-quality-attributes`)
1. **T24.1 Series.** If all n parts are needed and fail independently, A = ∏Aᵢ. Without independence you still have
   1 − Σ(1 − Aᵢ) ≤ A ≤ min Aᵢ: a chain is never stronger than its weakest link, and unavailabilities roughly add.
2. **T24.2 Parallel and k-of-n.** One of n independent replicas is enough: A = 1 − ∏(1 − Aᵢ). At least k of n identical
   replicas: a binomial tail.
3. **T24.3 Nines and steady state.** Allowed downtime is (1 − A)·T; each extra nine divides it by 10 (99.9 % ≈ 43.2 min per
   30 days, 99.99 % ≈ 4.3 min). For alternating up and repair periods, the long-run up fraction is MTTF/(MTTF + MTTR),
   whatever the distributions (renewal–reward theorem).
4. **T24.4 Break-even weight.** Score two options on two criteria with weights (w, 1 − w). The difference is linear in w,
   so the preferred option flips at most once, at w* = d₂/(d₂ − d₁), and only if each option wins one criterion.

## Intuition
Independence is the assumption that makes the arithmetic easy and the one that fails in practice. Two API replicas that
share one feature-flag store are not independent: P24-5 shows the tier's unavailability is about 41 times higher than the
naive formula suggests. The *Calculus of Service Availability* (Treynor et al., 2017) states the operational version:
a service cannot be more available than the intersection of its critical dependencies, so critical dependencies should
offer about one more nine than the service itself, or be mitigated (caches, graceful degradation, failing open).

Availability is also a *rate* problem. Three 20-minute outages a year are 60 minutes, already more than the 52.56 minutes a
99.99 % yearly target allows – however good the rest of the year is. That is why MTTR (detect, decide, restore) is usually
the cheaper lever: P24-6 shows a database that fails every 720 h reaches 99.95 % only if it is restored within 21.6 minutes.

Trade-off analysis is mostly about making judgement visible. ATAM does not try to predict quality precisely; its authors
describe it as a risk-identification method that finds where decisions matter. T24.4 adds one piece of rigour: if a choice
flips at a weight of 0.42 and stakeholders disagree around that value, record the weight in the ADR and treat it as a
sensitivity point.

## Worked example: a Library Loans request path
Stated (hypothetical, not measured) availabilities: load balancer 99.99 %, API instance 99.5 %, database 99.9 %, identity
provider 99.95 %. With one API instance, A = 99.341 % (about 285 minutes of downtime per 30 days). A second replica lifts
the API tier to 99.9975 % and the path to 99.838 %; a third adds only 0.002 points because the database (99.9 %) is now the
bound from T24.1. The lab checks the formula three ways: algebra, exact enumeration of all 32 up/down states, and a
400,000-trial Monte Carlo run within four standard errors. The utility tree in `tradeoff.py` ranks "primary database fails
at peak, restored within 5 minutes" as (H, H), the first place an evaluation should spend time.

## Common misconceptions
- **"Redundancy multiplies nines."** Only for independent failures; shared dependencies, shared deploys and shared regions
  break independence.
- **"Five nines is always better."** Each nine costs roughly ten times less downtime, often at much more than ten times the
  cost; users cannot tell the difference beyond the availability of their own network (Treynor et al.).
- **"Availability = uptime of the servers."** Measure it as users experience it: good requests / valid requests (lesson 15).
- **"Quality attributes are non-functional extras."** In ISO/IEC 25010:2023 they are the product quality model; inclusivity
  and safety sit beside performance and security.
- **"ATAM gives a score."** It gives risks, sensitivity points and trade-off points; the decision stays with people.
- **"A weighted sum settles a trade-off."** It moves the argument to the weights – which is useful only if you say so.

## Check yourself
1. Why does adding a third API replica barely help? 2. Turn "the system shall be accessible" into a scenario with a
response measure. 3. At what weight on availability does replicated PostgreSQL beat a single SQLite file in the lab, and
what would you write in the ADR about it?
