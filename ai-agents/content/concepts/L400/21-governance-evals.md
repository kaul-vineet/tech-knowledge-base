**Concept: governance and evaluation in production – pinned models, eval and red-team gates, drift, audit, retention**

## Why it matters
An agent that passed its tests last month can fail today without a single code change. Someone ran `ollama pull`, the tag now points at new weights, and one priority rule changed. Or the traffic changed: a shipping outage tripled delivery tickets. Governance is the set of controls that turn "we tested it once" into "we know what is running, we would notice a change, and we can show what happened". NIST AI 600-1 (the generative-AI profile of the AI RMF) asks for exactly this: pre-deployment testing, ongoing monitoring, incident records. This lesson implements each control as code with a test.

## Mental model
Five controls around one pinned model, each answering one question:

```
models.lock.json (name + digest) ── pin check at start ─────────── "is this the model we tested?"
candidate ──► golden-set gate (lesson 12) + red-team suite (16) ── "is the new one at least as good and safe?"
production ──► drift check on outputs/inputs (chi-square) ────────── "has the world or the model shifted?"
every step ──► hash-chained audit log ──────────────────────────── "who did what, when - provably?"
content ──► retention purge (30 days), chain kept ───────────────── "are we keeping personal text too long?"
upgrade ──► decision record filled from the report ─────────────── "why did we accept or reject it?"
```

## Design space
- **Upgrade checks.** Manual spot checks are cheap and miss things: lesson 12's v2 passed a 3-case spot check. A pass-rate gate is better, but a 95 % bar still lets one regression through. A per-case regression gate plus the red-team suite is stricter, and it needs a maintained golden set.
- **Monitoring.** Labelled online evals are the most accurate and the most expensive. Distribution drift needs no labels. NIST's chi-square goodness-of-fit compares this window's category or priority counts with a baseline: alarm when χ² is above the critical value (13.277 for 4 degrees of freedom at α = 0.01). It is cheap, but it sees only shifts large enough to move a distribution.
- **Audit and retention.** An append-only table can still be edited by anyone with write access. A hash chain makes any edit, deletion or reordering detectable. Data protection rules (GDPR storage limitation) require deleting personal text when it is no longer needed. Keep content and hashes apart, so deleting content keeps the chain intact.
- **Pinning.** A name like `qwen2.5:1.5b` is mutable. Ollama's `/api/tags` reports a digest per model; pin the digest and refuse to start on a mismatch.

## How to decide
Criteria: what a bad answer costs, how often models change, whether you have labels, and who must be able to audit. Evidence comes from replaying a known change through every control.

Worked example (lab → see lab steps 1-3): re-tagging `fake-model:latest` to v2 changed t14 from high to normal priority. The pin check reported `pinned 1f49242847a4, server has 52d1337ffaca`. For candidate v2: golden set 19/20 (95 %), regression t14 → **REJECT**. The red team was 8/8 safe. Output drift on 200 replayed tickets gave χ² = 3.92 (df 1), below 6.635: no alarm. That is the honest limit of drift checks. Input drift on a shipping surge gave χ² = 45.71 (df 4): alarm. Editing one audit row's actor made `verify()` fail at seq 3. A pass-rate-only gate would have accepted v2 (try it 1). The upgrade record is generated from these numbers. The model may draft the Context paragraph (agent assist), but any number not in the report rejects the draft, and the Status line is always computed by code.

## Failure modes at scale
- **Golden-set rot:** the set no longer reflects traffic, so the gate passes while users suffer. Watch drift alarms; add their tickets to the set.
- **Alert fatigue:** fixed-threshold drift on huge windows alarms on every small shift (χ² grows with n). Watch the alarm rate, and tune the window size or use effect-size bounds.
- **Retention that breaks audit:** deleting audit rows to meet retention destroys the evidence (build task). Watch `verify()` after every purge.

## Common mistakes
- Pinning by tag instead of digest.
- Letting a model, a dashboard or a person type the upgrade decision instead of computing it from the report.
- Logging full prompts forever "for debugging".
