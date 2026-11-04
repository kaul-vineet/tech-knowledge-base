# Model upgrade: {{pinned}} -> {{candidate}}

Status: {{decision}} (computed by `decide_upgrade()`; a person signs off, the model never sets this line)

## Context
{{context}}

## Evidence (measured, copied by code from the report)
| Check | Result | Required |
|---|---|---|
| Golden set (lesson 12 gate) | {{passed}}/{{total}} ({{pass_pct}}), regressions {{regression_count}}: {{regressions}} | no regression, pass rate >= 95 % |
| Gate reasons | {{gate_reasons}} | [] |
| Red-team suite, protected (lesson 16) | {{redteam_safe}}/{{redteam_total}} safe | all safe |
| Output drift on replayed traffic (chi-square, priority) | chi2 {{drift_chi2}}, df {{drift_df}}, alarm {{drift_alarm}} | no alarm at alpha 0.01 |

## Decision
{{decision}}: the candidate replaces the pinned model only if every row above meets its requirement.

## Consequences
- ACCEPT: update `models.lock.json` (name + digest) in the same change, re-run the CI gate, keep the old digest for rollback.
- REJECT: the lock stays; record the failing cases as new golden/red-team cases; re-evaluate the next candidate.
- Either way: keep this record next to the code (Nygard ADR: Title, Status, Context, Decision, Consequences).
