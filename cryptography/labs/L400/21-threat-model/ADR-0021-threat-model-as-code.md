# ADR-0021: Keep the threat model as code: STRIDE per element, controls proven by named tests, attack tree on verified controls

## Status
Accepted (2026-10-28, lesson 21 lab). Applies to every design in this topic and to the capstone (`22-capstone/threat_model.json`).

## Context
The topic now has envelopes, rotation, release signing, TLS and PQ key exchange, a key token and group keys. A
threat-model document drifts away from the code: tests are renamed, integrations are added, and nobody updates the
diagram. Three ways to find threats were compared on this topic's model (`threat_model.py`):
- STRIDE per element: 11 elements, 5 of them flows (4 cross a trust boundary), give 41 candidate (element, category) pairs; 18 threats are recorded and mapped to 12 controls.
- Attack tree: one attacker goal, 4 OR-branches. With every control verified, the cheapest open path is "phish an authorised user" (cost 9). Without any controls it is "stay in the project room after removal" (3).
- Agent brainstorming (`agent_assist.py`, fake model): of 6 proposals, 2 were confirmed, 1 is a real gap and 3 were rejected (an unknown element, a STRIDE letter that does not apply, an invented control).

Seeded drift (a deleted test plus a new SIEM export flow) was invisible to a checker that only checks control *names*:
`checker problems: []`.

## Decision
1. Keep the model in `model.json` next to the code: elements with trust zones, flows, threats (element, STRIDE letter, controls or a recorded acceptance), and controls that name tests as `file::Class::method`.
2. A control counts only if every test it names exists (checked through the AST) and passes (the fitness test runs them).
3. Coverage rules: every element has at least one threat, and every flow that crosses a trust boundary has T and I threats.
4. The attack tree closes a leaf only for verified controls, so a deleted test shows up as a cheaper attack path (8 instead of 9 in the lab).
5. An agent may propose threats. Code classifies each proposal as CONFIRMED, GAP or REJECTED, and nothing is merged automatically. The prompt carries only element names, and the secret gate checks it.
6. Fitness function: `test_fitness_threat_model.py` requires 0 checker problems and every referenced control test passing.

## Consequences
- The model breaks the build when it stops matching the code, which is the point, but someone must own fixing it.
- STRIDE per element produces many candidates (41 here). Only 18 became threats; the rest were judged not applicable, and that judgement lives in reviews, not in code.
- Attack-tree costs are the lab's own 1–10 scale. They rank paths; they are not probabilities.
- Running the control tests costs time: about 100 s on the sandbox's slow file mount, though only about 6 s of CPU. Run it in CI, not on every save.
- Accepted risks (T4, handshake floods) must name an ADR. Acceptance is a decision, not a missing row.
