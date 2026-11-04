**Concept: SLOs, error budgets and burn-rate alerts**

## Why it matters
"Mean latency below 200 ms" looks reasonable on a dashboard. From 10:30 one borrow in five takes almost
3 s, yet the mean stays at 148 ms, so no alert fires. Members feel the slow tail; averages hide it. SLOs
measure what users experience and answer one question: are we spending our error budget too fast?

## Mental model
The error budget is a monthly allowance of bad requests. A 99 % SLO allows 1 bad request in 100 over
30 days. The burn rate is the rate of spending: 1 means you run out exactly at the end of the month,
and 14.4 means 2 % of the month's budget gone in one hour.

```
request log (JSON lines) ─► SLI = good / valid ─► bad ratio per window ─► burn = bad ratio / (1 - SLO)
                                                     1h & 5m   ≥ 14.4 ─► page
                                                     6h & 30m  ≥ 6    ─► page
                                                     3d & 6h   ≥ 1    ─► ticket
```

## How it works
1. **SLIs come from structured logs.** Each request is one JSON line (`ts`, `route`, `status`, `ms`).
   An SLI is good events divided by valid events → see lab step 2
2. **Availability SLI:** status < 500 across all routes, SLO 99.9 % → see lab step 1
3. **Latency SLI as a threshold ratio:** "POST /loans succeeds in under 300 ms", SLO 99 %. Counting slow
   requests is the p99 view, and unlike a mean it cannot be averaged away → see lab step 5
4. **Multiwindow, multi-burn-rate alerts** (Google SRE Workbook, table 5-8): an alert fires only if both
   the long and the short window burn above the threshold. The long window gives significance; the short
   window, 1/12 of it, makes the alert reset soon after recovery → see lab step 3
5. **Budget consumed = burn rate × window ÷ period** → see lab step 1
6. **Agent assist:** a local model drafts the incident summary; code checks every number → see lab step 6

**Worked example** (`research/L300_concept_examples.py`): at 12:00 the last hour shows a mean of
147.9 ms, p95 94.3 ms and p99 2846.3 ms. The base mean check finds nothing. In the latency SLI, 19.7 %
of POST /loans were bad against a 1 % budget, so the burn rate is 19.7 (≥ 14.4) and the 1h/5m page
fires. That hour used 19.7 / 720 = 2.7 % of the 30-day budget. The workbook's time-to-fire formula
predicts 43.9 min; the lab paged after 57 min, because about 6 POST /loans per 5 minutes make the short
window noisy.

## Failure modes
- **Mean-based latency alerts** miss tails, and so does an overall p95 (94.3 ms here) when the slow route
  is a minority of traffic.
- **Low traffic:** short windows hold few requests; alerts flap or come late.
- **SLO too tight:** ignored alerts. Too loose: users complain first.
- **Bad log data:** missing routes or clock skew change the SLI silently.

## Common mistakes
- Alerting on causes (CPU, queue length) instead of symptoms users feel.
- Aggregating precomputed percentiles across instances. Count good and valid events instead.
- Letting a model compute or round the numbers in an incident report. Code computes; the model words it.
