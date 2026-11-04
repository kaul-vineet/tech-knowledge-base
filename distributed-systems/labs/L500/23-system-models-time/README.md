# Lesson 23 - Foundations I: system models, time and causality

Numerical checks for T23.1-T23.4: Lamport's clock condition (and its failing converse), vector clocks = happened-before, safety vs liveness on every trace up to length 8, and false suspicions of a timeout detector with and without a delay bound.

Stdlib only (Python 3.12+); seeded, so the output below is identical on every run and on macOS, Windows and Linux.
The same output is quoted as `checkOutput` in `content/L500.json`; `python research/l500_checks.py` (from the topic folder) fails if they drift apart.

## Run
```bash
python clocks_proofs.py              # all checks
python clocks_proofs.py <name>       # one check: clock | vector | safety | detector
python -m unittest -v        # test_clocks_proofs.py: smaller runs, same invariants
```

## Expected output (observed on Python 3.12, Linux)
```
T23.1 Lamport clock condition: 300 random executions, 3 processes, 54,600 ordered event pairs
  pairs with a->b: 13,599; violations of L(a) < L(b): 0
  (L, pid) total order: duplicate keys 0; a->b ordered the other way 0
  converse fails: 11,063 of 27,402 concurrent pairs still have L(a) < L(b)
  broken receive rule (tick only, no max): 990 violations
T23.2 vector clocks: same 300 executions, 54,600 ordered pairs
  mismatches between a->b and V(a) < V(b): 0
  concurrent pairs 27,402; incomparable vectors 27,402
  broken receive rule (no element-wise max): 4,546 mismatches
T23.3 safety vs liveness: all 9,841 traces over {req, resp, idle} up to length 8
  safety S = 'never more responses than requests': 3,292 good traces, 6,549 bad
  S prefix-closed: good traces with a bad prefix = 0
  bad traces repaired by any extension up to length 3: 0
  liveness L = 'every request eventually answered': good prefixes that cannot be completed = 0
T23.4 failure detection: round-trip heartbeat, live peer, 200,000 heartbeats each
  asynchronous model (Pareto alpha=1.5, min 1 ms, no upper bound): timeout -> false suspicions
        5 ms -> 17,960 (8.9800%); theory 8.9443%
       20 ms ->  2,180 (1.0900%); theory 1.1180%
      100 ms ->    194 (0.0970%); theory 0.1000%
     1000 ms ->      5 (0.0025%); theory 0.0032%
  synchronous model (one-way <= 50 ms, processing <= 5 ms): timeout 105 ms -> 0 false suspicions; max observed 104.4 ms
```

## What to look for
- Each line pairs a theorem's prediction with what the code observed. A proof says *always*; the check says *in every case we tried* - a counterexample would refute the proof, agreement only corroborates it.
- The *broken* variants (Lamport/vector clocks without the max, Paxos ignoring phase-1 values) show the proofs' assumptions are load-bearing.
- Simulation numbers carry sampling error; the lesson's problem set asks you to explain each gap.
