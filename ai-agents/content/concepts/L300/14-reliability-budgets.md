**Concept: reliability – timeouts, retries, budgets, fallbacks and caching around model calls**

## Why it matters
A local model server is a shared, overloaded resource: it answers 503 while a big model loads, stalls for seconds when the GPU is busy, and sometimes never answers. The happy-path agent loop has no timeout and retries anything, so one stall becomes a hung request and one runaway loop becomes a large bill. Reliability is deciding, in code, how long to wait, what to retry, how much to spend and what to say when all else fails.

## Mental model
A circuit with fuses. Each call has its own fuse (timeout), the whole question has a main fuse (budget), and there is a spare line (fallback model) plus a recorded message (canned answer) when the power is out.

```
question ─► cache? ─hit─► answer
              │miss
              ▼
 primary ─► [timeout 0.5 s] ─5xx/timeout─► backoff+jitter ─► retry (max 2) ─► give up
              │ok                                                              │
              ▼                                                                ▼
           budget.add(tokens, $) ── over budget ─► canned answer ◄── fallback model fails
```

## How it works
1. **Per-call timeout.** `requests.post(..., timeout=0.5)`; without it a stalled server holds the agent for as long as it likes. → see lab step 1
2. **Retry only what can succeed later.** 5xx and timeouts are transient; a 4xx means our request is wrong and is raised at once (`test_4xx_is_not_retried`). → see lab step 3
3. **Backoff with jitter.** Delay = min(cap, base · 2^attempt) · U(0.5, 1). With base 0.05 s, cap 0.4 s and seed 7 the schedule is 0.033, 0.058, 0.165, 0.214 s – growing, capped, and never in lock-step with other clients. → see lab step 2
4. **Budgets.** Every attempt – step or retry – spends from one per-question `Budget`: 8 calls, 1,500 tokens, $0.01. A question that needs 9 calls ends in the canned answer instead of running on. → see lab step 1
5. **Fallback and cache.** After the primary gives up, the same request goes to a smaller model on another endpoint; identical requests are served from a response cache with 0 calls and 0 tokens. → see lab step 2
6. **Worked example.** Ten questions against a seeded server (30 % 503, 20 % +2 s). Naive loop: slowest question about 6 s, 269 tokens. Hardened: slowest under 2 s, 132 tokens, 3 fallbacks, 2 cache hits, 1 canned answer (the 9-call question). → see lab step 1

## Failure modes
- **Retry storm:** every client retries at once without jitter or a budget, keeping the server overloaded; you see request rate rise while success rate falls.
- **Timeout shorter than real work:** long answers are cut every time and retried forever; `retry` events show the same `ms` close to the timeout.
- **Fallback that is just as broken:** both endpoints share one GPU; fallbacks rise but the canned rate does not fall.
- **Stale cache:** cached answers outlive the data they used; key the cache on everything that changes the answer and set a lifetime.
- **Hidden cost:** retries spend tokens too; the budget must count them.

## Common mistakes
- Retrying non-idempotent tool calls the same way as model calls (lesson 15).
- Using the same timeout for a 1-token classification and a 2,000-token answer.
- Returning an exception to the user instead of a planned fallback message.
