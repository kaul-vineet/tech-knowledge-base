# 3. Run validation replications in a checkpointed parallel runner, and publish only with a checked model card

## Status
Accepted (2026-10-28)

## Context
The plan is validated by 24 full-day replications. Those runs must be reproducible on the Mac mini, the Windows PC and CI, whatever the worker count and whether or not a run was interrupted. The decision is advisory (the duty manager signs off), so a light, machine-checked model card fits (lesson 21). Measured: crash after 10 results + resume on 1 worker gives the same checksum as a clean run on 2 workers. The card's claims (lognormal, holdout errors ≤ 1.5 / 1.0 pp, rates ≤ 5.6/min, hashes of `centre.py`, `pipeline.py` and the KPI data) have no findings against this run's evidence.

## Decision
Reuse the lesson 20 pattern: SQLite with WAL, a key per replication, `SeedSequence(22, spawn_key=(rep,))`, batches of 8. Publish a recommendation only when `governance_pack.check()` returns no findings. Plans outside the envelope carry review flags, and an agent explanation is published only if every number in it is verified.

## Consequences
- Any edit to the DES or the pipeline stales the card until it is regenerated: deliberate friction.
- Review flags do not block the decision: code decides, people sign off.
- Fitness functions: `test_fitness.py::test_sla_holds_for_the_recommended_plan` (1 vs 2 workers give an identical checksum) and `test_governance_card_is_current`.
