# ADR-0021: Models are pinned by digest and upgraded only through the eval + red-team gate

## Status
Accepted (2026-10-28). Kept true by `test_fitness_governance.py`.

## Context
A local model is a name that can point to new weights after a pull. In the lab, re-tagging `fake-model:latest` changed the answer for t14 from high to normal priority with no code change. For the candidate `fake-model:v2`, `governance.py` measured: golden set 19/20 (95 %, the pass-rate bar holds) but one regression (t14); red team 8/8 safe; output drift on 200 replayed tickets chi2 3.92 (df 1, no alarm at alpha 0.01). A category drift check did fire on a shipping surge (chi2 45.71, df 4). NIST AI 600-1 asks for pre-deployment testing, ongoing monitoring and incident records for generative AI.

## Decision
We will pin every model by name and digest in `models.lock.json` and refuse to start on a mismatch. A model upgrade is ACCEPTED by code only if the golden-set gate has no regression, the red-team suite is fully safe and the replay drift check raises no alarm; the record is filled from the measured report (template `MODEL-UPGRADE-TEMPLATE.md`). Production keeps a hash-chained audit trail and runs weekly category drift checks; prompt text is deleted after 30 days while the chain of hashes is kept.

## Consequences
- A pass-rate-only gate would have accepted v2 (try it 1); the per-case regression check is the part that matters.
- Drift checks are coarse: they caught a 3x input shift, not a 1-case behaviour change; they complement the golden set, not replace it.
- Retention deletes content, not audit rows; investigations after 30 days see who/what/when but not the prompt.
