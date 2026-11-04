## Why it matters
The payment service hangs. Checkout has no timeout, so every worker thread waits on it, new customers queue behind them, and one slow dependency takes your whole service down.

## Mental model
A timeout is a kitchen timer set before you phone: when it rings you hang up and free the line. A deadline is that timer written as a clock time, whose remainder you pass on.

```
A ── call B ─── 0.5 s ─── ✖ timeout → thread freed, error/fallback
budget 2.0 s → A spends 0.5 s → calls C with timeout 1.5 s
```

## How it works
1. **Every remote call gets a limit.** `urlopen` without `timeout` waits as long as B takes; with `timeout=0.5` it raises `TimeoutError` after ~0.5 s — while B keeps working. → see lab step 1
2. **Pick the value from data.** Accept a false-timeout rate (0.1%) and use the matching percentile: B's p99.9 = 116 ms gives a 0.116 s timeout. → see lab step 3
3. **Stricter is not free.** A 1% false-timeout rate means p99 = 0.088 s: a shorter wait, but about 1 in 100 normal requests is cut off. → see lab step 4

## Common mistakes
- No timeout, or one fixed 30 s value everywhere instead of per-dependency values.
- Each hop restarting a full timeout instead of passing the remaining budget (tryIt 2).
- Assuming the timeout cancelled the work on the server.
