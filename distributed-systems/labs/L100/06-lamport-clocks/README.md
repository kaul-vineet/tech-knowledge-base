# 06 · Ordering events with Lamport clocks

Three nodes (A, B, C), each an HTTP server, exchange messages that carry a Lamport timestamp. Each node's wall clock is deliberately skewed (B −80 ms, C +40 ms). Sorting the event log by wall clock shows receives *before* their sends; sorting by `(Lamport, node id)` never does.

Files: `lamport.py` (the lesson code: the three clock rules), `helpers.py` (plumbing + `violations()`/`show()` log printing), `try_it.py` (tryIt experiments), `test_lamport.py`.

## Run
```bash
python lamport.py
```

## Expected output (real run, Python 3.12.15, Linux — identical on every run; simulated time)
```
--- sorted by wall clock: 2 causality violation(s) ---
  L=3  wall=-0.050s  B: recv 'create order' from A
  L=4  wall=-0.040s  B: reserve stock
  L=5  wall=-0.030s  B: send 'charge card' to C
  L=1  wall=+0.010s  A: user clicks Buy
  L=2  wall=+0.020s  A: send 'create order' to B
  L=8  wall=+0.080s  A: recv 'payment ok' from C
  L=6  wall=+0.100s  C: recv 'charge card' from B
  L=9  wall=+0.100s  A: show receipt
  L=7  wall=+0.110s  C: send 'payment ok' to A
  L=8  wall=+0.130s  C: write audit log
--- sorted by (Lamport, node): 0 causality violation(s) ---
  L=1  wall=+0.010s  A: user clicks Buy
  L=2  wall=+0.020s  A: send 'create order' to B
  L=3  wall=-0.050s  B: recv 'create order' from A
  L=4  wall=-0.040s  B: reserve stock
  L=5  wall=-0.030s  B: send 'charge card' to C
  L=6  wall=+0.100s  C: recv 'charge card' from B
  L=7  wall=+0.110s  C: send 'payment ok' to A
  L=8  wall=+0.080s  A: recv 'payment ok' from C
  L=8  wall=+0.130s  C: write audit log
  L=9  wall=+0.100s  A: show receipt
```
`L=8` appears twice: A's receive and C's audit log are concurrent; the node id breaks the tie.

## Test
```bash
python -m unittest -v          # Ran 4 tests ... OK
```

## Note
Lamport order is *consistent with* causality (if a caused b then L(a) < L(b)), but L(a) < L(b) does not prove a caused b. To detect concurrency you need vector clocks (L200).

## Try it (real run, Python 3.12.15, Linux — simulated time, identical on every run)
```bash
python try_it.py
```
```
tryIt 1: without max(): m1 send L=2, recv L=1; (Lamport, node) order has 2 violation(s)
tryIt 2: B  5 ms slow -> wall-clock order 0 violation(s), (Lamport, node) order 0
tryIt 2: B 15 ms slow -> wall-clock order 1 violation(s), (Lamport, node) order 0
```
