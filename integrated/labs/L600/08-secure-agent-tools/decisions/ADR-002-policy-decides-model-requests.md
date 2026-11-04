# ADR-002: The model requests tool calls; a deny-by-default policy decides; high risk waits for a human

## Status
Accepted (2026-10-30). Fitness: F1 in `tests/test_fitness.py`; seams `tests/test_seam_model_policy.py`, `tests/test_seam_output_tagging.py`.

## Context
Indirect prompt injection (Greshake et al. 2023) puts instructions inside data the agent reads. In the failure lab a
poisoned doc makes the model request `send_email` to an attacker; the naive host sends it. Across the seeded corpus
the fake model obeyed 24 of 40 payloads and the naive host executed all 24 (16 side effects). Output tagging and a
system prompt did not change the model's request - the shared fake, like many real models, obeys anyway.

## Decision
We will treat every model output as a REQUEST. The host computes the policy input itself (tool facts from the
signed manifest, scope from the token, schema validity, user provenance of target arguments) and evaluates
`policy/tools.rego` (application-architecture L400 #19's engine): allow only via an allow rule with no deny;
high-risk tools additionally need a human `yes` that sees the exact tool and arguments. Tool output is escaped and
wrapped in `<untrusted_data>` as defence in depth, never as the control.

## Consequences
- 0 of 40 injected calls executed; legitimate in-scope work still runs (S1, S3, S4).
- Denied calls never reach the approver, so injections cannot cause approval fatigue.
- Provenance by substring is strict: a user who paraphrases a target ("email Alice") gets a denial and must name it.
- The policy revision hash is logged with each decision, so decisions can be replayed after a policy change.
