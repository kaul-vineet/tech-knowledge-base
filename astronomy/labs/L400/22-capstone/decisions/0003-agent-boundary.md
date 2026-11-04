# 3. A local model may explain a vetted candidate; it never decides, and its text is gated by code

## Status
Accepted (2026-10-29)

## Context
The team wants a plain-language note per candidate. Language models write fluent text, but they also invent numbers and over-claim. Here, the fake model invents "1.8 Earth radii" and calls every candidate "a planet". Verdicts must stay reproducible and auditable (ADR 0002), and the light curves and any credentials must stay on the machine.

## Decision
`agent_explain.py` sends only a facts block (star, period, depth, verdict, reasons) to a local OpenAI-compatible endpoint (`LOCAL_MODEL_URL`, `LOCAL_MODEL`; Ollama on the Mac mini or the Windows PC). The explanation is published only if every number in it appears in the facts and it does not call a rejected candidate a planet. The verdict is computed before the model is called and is never read back from it.

## Consequences
- With the fake model, all 6 explanations (stars with SNR ≥ 10) are blocked. S04, S05 and S06 are blocked as over-claims, and all are blocked for the number "1.8". The verdicts are unchanged.
- A real model will sometimes pass the gate with wording we did not anticipate. The gate checks numbers and one claim pattern, not meaning, so a human still reads published notes.
- No model is needed for the science result. `run_capstone.py` passes M1–M5 without one.
- Fitness: M6 in the scorecard and `test_fitness.py::test_scorecard_pass_and_agent_gated`.
