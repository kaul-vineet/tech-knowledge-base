# Lesson 24 - Foundations II: impossibility results and consensus

Numerical checks for T24.1-T24.4: a bounded family of two-generals protocols (all fail), duelling Paxos proposers under an adversarial schedule (FLP illustrated), Gilbert & Lynch's CAP execution against three register designs, exhaustive quorum intersection for N <= 7 and 3,000 randomised single-decree Paxos runs (plus a broken variant).

Stdlib only (Python 3.12+); seeded, so the output below is identical on every run and on macOS, Windows and Linux.
The same output is quoted as `checkOutput` in `content/L500.json`; `python research/l500_checks.py` (from the topic folder) fails if they drift apart.

## Run
```bash
python consensus_proofs.py              # all checks
python consensus_proofs.py <name>       # one check: generals | flp | cap | paxos
python -m unittest -v        # test_consensus_proofs.py: smaller runs, same invariants
```

## Expected output (observed on Python 3.12, Linux)
```
T24.1 two generals: 140 protocols (M = 0..6 messengers, every threshold pair)
  protocols with a disagreeing or never-attacking run: 140; correct protocols: 0
  e.g. M=2, tA=1, tB=1: 1 delivered: A waits, B attacks
  e.g. M=6, tA=3, tB=3: 5 delivered: A waits, B attacks
T24.2 FLP illustrated: 2 proposers, 3 acceptors, adversarial schedule for 1000 rounds
  ballots started 2000, accepts issued 2000, acceptances 0, values chosen 0 (safe, never live)
  with random backoff U[0, 4) after a clash (a timing assumption): 10,000 runs, all decided: True, mean attempts 4.35, max 37
T24.3 CAP: partition {n1} | {n2}, all messages between the groups lost; write v1 @n1, then read @n2
  AP-local               ok                               read -> v0                                   available=True linearizable=False
  AP-sync-then-timeout   ok                               read -> v0                                   available=True linearizable=False
  CP-majority            no response (needs 2 of 3 acks)  read -> no response (needs 2 of 3 replies)   available=False linearizable=True
T24.4 quorum intersection, exhaustive for N = 1..7, every (R, W):
  21,343 (read quorum, write quorum) pairs checked
  R + W > N with a disjoint pair: 0; R + W <= N configurations with a disjoint pair: 56 of 56
  correct single-decree Paxos     : 3000 random runs (loss 15%, dup 10%, reorder), decided 3000, runs with 2 values chosen 0, runs violating P2b 0
  broken (ignores phase-1 values): 3000 random runs (loss 15%, dup 10%, reorder), decided 3000, runs with 2 values chosen 2296, runs violating P2b 2498
```

## What to look for
- Each line pairs a theorem's prediction with what the code observed. A proof says *always*; the check says *in every case we tried* - a counterexample would refute the proof, agreement only corroborates it.
- The *broken* variants (Lamport/vector clocks without the max, Paxos ignoring phase-1 values) show the proofs' assumptions are load-bearing.
- Simulation numbers carry sampling error; the lesson's problem set asks you to explain each gap.
