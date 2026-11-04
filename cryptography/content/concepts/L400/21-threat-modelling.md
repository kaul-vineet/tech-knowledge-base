## Why it matters
Correct primitives and tested labs still leave the question: what can go wrong *in this system*? Threat modelling answers OWASP's four questions: what are we working on, what can go wrong, what are we going to do about it, and did we do a good enough job? For cryptographic systems the dangerous answers are rarely "AES is broken". They are a key that is readable, a downgrade that is accepted, a log that can be edited, or a control whose test was deleted in a refactor. A threat model that lives in a slide deck drifts. A model that lives next to the code, and fails the build when it stops matching, keeps paying off.

## Mental model
A **map, a checklist and receipts**. The map is a data-flow diagram: external entities, processes, stores, flows, and trust boundaries between zones. The checklist is STRIDE applied per element: Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege, each a violated property (authentication, integrity, accountability, confidentiality, availability, authorisation). The receipts are the tests: every threat points to a control, and every control points to tests that exist and pass.

```
threat T8 (doc-api→envelope-db, Tampering) ─► control C-DUAL-SIG ─► test_build_task.py::…::test_stripped_envelope_rejected…
attack tree: goal ─OR─ steal key (AND: host 5 + read key 1 [C-NONEXPORT])
                   └── harvest (AND: record 2 + fallback 1 [C-NO-FALLBACK] + quantum 5) …
```

## Design space
- **STRIDE per element.** Systematic and good for coverage: every element type has its applicable letters (this lab: external S,R; process all six; store and flow T,I,D). It produces many candidates, and judging them takes people.
- **Attack trees.** Start from an attacker goal and decompose it into AND/OR steps with costs. They show which control matters most and turn "a test was deleted" into "the cheapest attack got cheaper".
- **Misuse cases and LINDDUN** cover business-logic abuse and privacy. Use them when they fit, and record which concerns each technique does not address (OWASP).
- **Agent brainstorming.** Fast and broad, but it invents elements and controls. Code must classify each proposal.

## How to decide
Criteria: coverage of elements and boundaries, traceability from threat to test, how drift gets noticed, and the effort for the team.

Evidence from `threat_model.py` on this topic's designs (→ see lab steps 1-3):
- 11 elements, 5 of them flows (4 cross a boundary), give **41** STRIDE-per-element candidates; 18 threats are recorded and mapped to 12 controls, all of whose tests exist.
- The attack tree's cheapest open path with every control verified is "phish an authorised user" (cost 9). With no controls it is "stay in the project room after removal" (3).
- The agent assist (fake model) proposed 6 threats: 2 CONFIRMED, 1 GAP (no control yet), 3 REJECTED (an unknown element, a STRIDE letter that does not apply to a flow, an invented control).

Worked example from one lab run (→ see lab step 4). Seeded drift deletes the test behind `C-NO-FALLBACK` and adds a `app-log→siem` flow nobody modelled. The naive checker, which only checks that control *names* exist, reports `[]`. The fixed checker reports the missing test and the unmodelled boundary flow lacking T and I threats. Because only verified controls close attack-tree leaves, the cheapest path becomes the harvest-now path at cost **8**. tryIt 2 shows the same effect for `C-NONEXPORT`: cost 6 via host compromise. The fitness test then *runs* all 12 referenced tests.

## Failure modes at scale
- **Model drift.** New integrations and refactors are not reflected, which you see as flows without threats or controls without tests. Make both a build failure.
- **Checklist theatre.** Hundreds of candidates are marked "N/A" without thought. Keep acceptances explicit, with an ADR reference (T4 in the lab).
- **Untested controls.** "We use TLS" is not a control until a test fails when TLS is off (L200 #10's mTLS test). Map every control to a test that would catch its removal.
- **Agent-generated noise.** Unverified proposals inflate the model. Merge nothing automatically; triage GAPs by hand.

## Common mistakes
- Modelling the happy path only: forgetting stores such as logs and backups, and outbound flows such as SIEM exports.
- Ranking threats by gut feel without an attacker-goal view. Attack trees make the trade-off between controls visible.
- Writing the model once at design time. It has to change in the same pull request as the code.
