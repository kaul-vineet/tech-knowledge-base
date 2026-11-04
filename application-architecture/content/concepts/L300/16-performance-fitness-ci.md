**Concept: Performance and architecture fitness functions in CI**

## Why it matters
A refactor makes the overdue report "more readable": load the loans, then look up each member and book.
Output is identical; unit tests pass. With 500 loans, the report now sends 337 SQL statements
instead of 1. Nobody notices with in-process SQLite. In production, with a network round trip per
statement, the page takes a third of a second. Qualities such as query count, boundaries and
latency erode one commit at a time unless the pipeline measures them.

## Mental model
A fitness function tests an architectural characteristic, not a feature: an objective pass/fail on one
quality, such as "statements per report do not grow with the data". Deterministic, cheap gates run on
every commit; noisy timing gates get generous budgets.

```
commit ─► unit tests ─► fitness.py ─┬ import-boundaries   (ast)              deterministic
                                    ├ query-count ≤ 2     (sqlite3 trace)    deterministic
                                    ├ micro-benchmark     (timeit, min)      noisy → generous budget
                                    └ response-time p95   (load test / k6)   noisy → generous budget
                       exit 1 ─► build red
```

## How it works
1. **Gates print JSON lines** (`gate`, `ok`, `value`, `budget`), and the exit code is the contract with
   CI → see lab step 1
2. **Query counting.** `Connection.set_trace_callback` sees every statement SQLite executes. The gate runs
   the report on 10 and on 500 loans: a count that grows with the data is an N+1 → see lab step 2
3. **Import boundaries.** `ast` lists the imports of `domain.py`; `sqlite3`, `http` or the adapters fail
   the gate, the same rule as lessons 3 and 7 and import-linter → see lab step 1
4. **Micro-benchmarks with `timeit`.** `repeat()` several times and keep `min()`, the least disturbed run,
   as the Python docs advise → see lab step 4
5. **Load test with a response-time budget.** Four threads send 40 requests and the gate checks p95
   ≤ 200 ms with 0 errors. `k6/overdue.js` expresses the same budget as k6 thresholds
   (`p(95)<200`) → see lab step 5
6. **Fix and prove.** One JOIN brings the count to 1 for any number of loans, and the same rows come
   back → see lab step 3

**Worked example** (`research/L300_concept_examples.py`): the N+1 version sends 11 statements for 10 loans
and 337 for 500 (1 + 2 × 168 overdue). The JOIN sends 1 and 1. In the failure lab, both versions pass
the p95 budget (65–100 ms). With ≥ 0.5 ms added per statement to simulate a network database, the N+1
report takes about 343 ms and the JOIN 2.7 ms.

## Failure modes
- **Timing gates miss it:** small test data and an in-process database make N+1 cheap, so only the
  count is a reliable signal.
- **Flaky budgets:** tight timing budgets on shared CI runners fail at random; teams then delete the gate.
- **Gate drift:** budgets get raised to turn a build green. Record each change in an ADR.
- **Blind spots:** `ast` misses `importlib` string imports (lesson 3).

## Common mistakes
- Comparing means of benchmark runs across machines. Compare `min()` on the same runner, or ratios.
- Load-testing without a warm-up or with a tiny listen backlog: the lab's first runs measured 1 s
  connection retries.
- Treating fitness functions as a one-off audit instead of a CI gate on every change.
