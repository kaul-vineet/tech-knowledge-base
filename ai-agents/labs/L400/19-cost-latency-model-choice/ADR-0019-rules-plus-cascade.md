# ADR-0019: Ticket triage on the small model, escalated by rules and validation; stable prompt prefix first

## Status
Accepted (2026-10-28). Kept true by `test_fitness_cost.py`.

## Context
Triage runs on a Mac mini or a Windows PC. On the 20-case golden set (lesson 12), with relative compute units (about 2 x parameters per token, cached prompt tokens at 10 %) and a warmed prefix cache:

| Strategy | Passed | Cost | p50 / p95 latency (estimate) | Escalated |
|---|---|---|---|---|
| Large only (stands in for qwen2.5:7b) | 20/20 | 7,000.0 | 867.8 / 883.2 ms | - |
| Small only (stands in for qwen2.5:1.5b) | 13/20 | 1,590.0 | 182.1 / 249.7 ms | - |
| Cascade: small, then large if code rejects the JSON | 19/20 | 3,807.6 | 182.1 / 1,132.9 ms | 6 |
| Rules + cascade (urgent/asap/immediately/down -> large) | 20/20 | 3,890.1 | 182.1 / 1,123.6 ms | 4 |

The cascade cannot see t03: the small model returns valid JSON with the wrong priority. FrugalGPT and RouteLLM report the same pattern: cascades and routers cut cost only as far as their scoring catches errors. Putting the stable instructions first makes 76 % of prompt tokens cacheable (3 % with the ticket first).

## Decision
We will send tickets to the small model, route tickets that match the rule learned from eval failures straight to the large model, and escalate to the large model whenever the structural validator rejects the small model's answer. Prompts keep instructions first and the variable ticket last.

## Consequences
- Cost is 56 % of large-only at equal golden-set accuracy; the routing rule must be re-learned when the golden set or the model changes (run the fitness test).
- Latency p95 grows to about 1.1 s for escalated tickets.
- Hardware: both models fit the base Mac mini (16 GB) with a 4k context; 14B at 32k x 4 slots does not fit 24 GB (sizing.py).
