# 4. The agent proposes and explains; the validator decides

## Status
Accepted (2026-10-30)

## Context
A local model can draft a plan or explain trade-offs in plain words, but it does not compute altitudes reliably.
The fake model used here drafts the typical naive plan: priority order, back to back from dusk, windows ignored,
one time written as local wall clock without a zone. The validator rejects 4 problems (1 unzoned time, Betelgeuse at
-16.4 deg, Fomalhaut at airmass 2.62, Deneb at airmass 6.50).

## Decision
- Agent text is parsed into `UtcInstant` rows (unzoned -> rejected) and judged by `validator.validate`, which
  recomputes altitude by an independent route (apparent sidereal time) every 5 minutes, plus Sun, Moon, overlap,
  grid alignment and duplicates. It never repairs a plan.
- An agent plan is adopted only if it has zero violations AND promises at least the optimiser's expected value.
- Explanations are published only if every number is in the facts block and every named star is a requested target.
- No secrets or credentials in prompts; the model has no tools and cannot trigger the telescope.

## Consequences
- A valid agent plan (the optimiser's plan written in +05:30 time) is accepted - the gate is not "reject all".
- Real models (Ollama) are tested in CI only; the fake keeps local runs deterministic.
