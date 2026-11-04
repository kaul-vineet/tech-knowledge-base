# 03 · Timeouts

B sleeps 2 s. A without a timeout waits the full 2 s (and would wait forever if B never answered); A with `timeout=0.5` fails after 0.5 s. Then a timeout is chosen from B's latency percentiles (seeded stand-in data).

Files: `timeouts.py` (the lesson code), `helpers.py` (plumbing: quiet handler, `reply()`, background server), `try_it.py` (tryIt experiments), `test_timeouts.py`.

## Run
```bash
python timeouts.py
```

## Expected output (real run, Python 3.12.15, Linux)
```
B takes 2.0 s to answer.
A timeout=None -> 200 ok               after 2.0 s
A timeout=0.5  -> FAILED TimeoutError  after 0.5 s
B latency: p50=40 ms  p99=88 ms  p99.9=116 ms
suggested timeout for A->B: 0.116 s
```
The percentile lines are seeded (`random.Random(7)`) and identical on every run.

## Test
```bash
python -m unittest -v          # Ran 3 tests ... OK
```

## Note
`urlopen(timeout=…)` applies to each blocking socket operation (connect, each read), not to the whole request. A server that trickles bytes can keep a call alive longer. For a hard end-to-end budget, track a deadline yourself (or use a client whose timeout covers the whole exchange, e.g. Go `http.Client.Timeout`).

## Try it (real run, Python 3.12.15, Linux)
```bash
python try_it.py
```
```
tryIt 1: delay=0.05 timeout=0.1 -> 200 ok
tryIt 1: delay=0.2  timeout=0.1 -> FAILED TimeoutError
tryIt 2: call 1 timeout=0.5 s -> 200 ok after 0.3 s
tryIt 2: call 2 timeout=0.2 s -> FAILED TimeoutError after 0.2 s
```
