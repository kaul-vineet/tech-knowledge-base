**Concept: model governance - documentation, V&V evidence and versions that a machine can check**

## Why it matters
A staffing model that worked in March is quietly edited in May, fed a new data file in June and quoted in a board paper in July. Nobody can say which version produced the number, what it was validated for, or whether the card's claims were ever true. Sargent (WSC 2010) defines validation as substantiating that a model "within its domain of applicability possesses a satisfactory range of accuracy consistent with the intended application". Each part of that definition is a claim that can be checked: the domain, the accuracy and the purpose.

## Mental model
A model card is a set of claims. Evidence is what the code measured. Governance is the diff between them.

```
verification.py --\
validate() vs Erlang C --> evidence.json --+
sensitivity()     --/                      +--> check_card() --> [] publish | [findings] block
sha256(code, data) -----------------------/          ^
                                     model_card.json (purpose, envelope, accuracy, versions)
```
Verification asks whether the code implements the model (degenerate tests, extreme conditions, internal validity: Sargent's technique list). Validation asks whether the model is accurate enough for this purpose within this envelope. Sargent's step 2 says to fix the required accuracy *before* the runs.

## Design space
- **A. Prose documentation.** A README with purpose and assumptions. It is quick and readable, and it is never checked, so it rots.
- **B. Structured model card + machine-checked claims.** A JSON card with an envelope, accuracy, key input, test count and code and data hashes, checked against freshly generated evidence in CI. Model cards come from Mitchell et al. (2019); this is their simulation-model cousin.
- **C. Full risk-informed credibility assessment.** NASA-STD-7009B (2024) and the FDA's 2023 guidance (following ASME V&V 40: model risk = model influence × decision consequence) scale the rigour of V&V to the decision's stakes. It is thorough and largely human-judged, and it is the right choice for safety-relevant decisions.

## How to decide
Criteria: what fraction of false claims an automated gate catches, the cost per release, and whether the rigour matches the decision's consequence (advisory staffing, reviewed by a manager: medium).

**Worked example (lab run).** Verification: 7 tests, 0 failures. Validation used 10 replications × 20,000 patients against the exact Erlang C answer, with a 10% requirement on both error and CI half-width. ρ 0.50-0.85 passed (worst error 5.5%). At ρ 0.90 the relative CI was 11.9%, which fails, so the envelope is utilisation ≤ 0.85. The busiest hour in `arrivals.csv` needs 0.80, so it is covered. Sensitivity: elasticity of Wq to λ 6.01 and to μ -7.02, so μ is the most influential input. A hurried draft card claimed 0.95, 2.0% error, λ as the key input and an old code hash. The shipped heading-only check called it **PUBLISHABLE**. The fixed `check_card()` found 4 findings. With a 5% accuracy requirement the envelope shrinks to 0.5, and appending one data row makes the card stale (`data_sha256`). **Decision (ADR 0001):** option B, with C's checklist items mapped onto it. `test_fitness.py` re-runs the evidence and blocks the build on any finding.

## Failure modes at scale
- **Many models, one template:** checks drift from the claims they guard. Generate the card's numeric fields from the evidence and let humans write the prose.
- **Stochastic evidence:** a re-run can move a value across a threshold. Fix the seeds and report CIs, so that a changed number means changed code.
- **Hash pinning is brittle:** every refactor stales the card. That is intended: bump the SemVer version (semver.org: released contents "MUST NOT be modified") and re-run.
- **Agent-written cards:** fluent text overclaims. The lab's local model claimed "utilisation up to 0.95" and "within 2.0%". Both were caught, and the agent's draft was rejected by code.

## Common mistakes
- Setting the accuracy requirement after seeing the results.
- Calling a model "validated" without stating the envelope.
- Checking that headings exist instead of checking that the numbers are true.
