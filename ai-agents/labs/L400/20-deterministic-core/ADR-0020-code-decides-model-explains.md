# ADR-0020: Refund decisions are made by code; the model may only propose claims and explain

## Status
Accepted (2026-10-28). Kept true by `test_fitness_invariance.py`.

## Context
Twelve refund requests, four with text that tries to steer the model. Measured with `edge.py`:

| Design | Wrong decisions |
|---|---|
| Model decides from the policy text | 6/12 (c02, c04, c05, c06, c08, c09); c08 approved 120.00 on an 80.00 order |
| Model decides; code validates schema, allow-list and amount | 5/12 (only c08's out-of-range amount was caught) |
| Code decides from system-of-record facts; model proposes claims and explains | 0/12 |

Validation stops answers that are malformed or out of range, not answers that are valid but wrong. Beurer-Kellner et al. (2025) describe the same separation as design patterns with provable resistance to prompt injection; the LPC1768 guide's rule is the same: thresholds in code, the model explains.

## Decision
We will compute every decision with `policy.decide(facts)`, using only facts from the order system. Model claims are untrusted: they can only move approve_auto to escalate. Model explanations are shown only when code can check that they name the decided action, no other action, and no other amount; otherwise a template is shown. Any model failure falls back to the decision plus the template.

## Consequences
- Changing a decision means changing code, with review and tests (try it 1: AUTO_LIMIT 150).
- The model's value is in reading free text (claims) and wording; losing the model loses wording, not decisions.
- The explanation check is conservative: some correct but unusual wordings fall back to the template.
